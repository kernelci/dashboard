from typing import TypedDict
from datetime import datetime
from django.db import connection

from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.typeModels.hardwareDetails import CommitHead, Tree


def _get_hardware_tree_heads_clause(*, id_only: bool) -> str:
    """Returns the tree_heads for the hardware queries,
    where the checkout is not filtered by origin.

    This is done because tests from a origin can be
    related to checkouts from another origin."""
    if id_only is True:
        fields = "C.id"
    else:
        fields = """C.id,
                    C.origin,
                    C.tree_name,
                    C.start_time,
                    C.git_repository_branch,
                    C.git_repository_url,
                    C.git_commit_name,
                    C.git_commit_hash,
                    C.git_commit_tags"""

    return f"""SELECT DISTINCT
                    ON (
                        C.tree_name,
                        C.git_repository_branch,
                        C.git_repository_url,
                        C.origin
                    )
                    {fields}
                FROM
                    checkouts C
                WHERE
                    C.start_time >= %(start_date)s
                    AND C.start_time <= %(end_date)s
                ORDER BY
                    C.tree_name ASC,
                    C.git_repository_branch ASC,
                    C.git_repository_url ASC,
                    C.origin ASC,
                    C.start_time DESC"""


# TODO: unify with get_tree_listing_count_clause
def _get_hardware_listing_count_clauses() -> str:
    build_count_clause = """
    COUNT(DISTINCT CASE WHEN "build_status" = 'PASS' AND build_id
        NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS pass_builds,
    COUNT(DISTINCT CASE WHEN "build_status" = 'FAIL' AND build_id
        NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS fail_builds,
    COUNT(DISTINCT CASE WHEN "build_status" IS NULL AND build_id IS
        NOT NULL AND build_id NOT LIKE 'maestro:dummy_%%' THEN build_id END)
        AS null_builds,
    COUNT(DISTINCT CASE WHEN "build_status" = 'ERROR' AND build_id
        NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS error_builds,
    COUNT(DISTINCT CASE WHEN "build_status" = 'MISS' AND build_id
        NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS miss_builds,
    COUNT(DISTINCT CASE WHEN "build_status" = 'DONE' AND build_id
        NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS done_builds,
    COUNT(DISTINCT CASE WHEN "build_status" = 'SKIP' AND build_id
        NOT LIKE 'maestro:dummy_%%' THEN build_id END) AS skip_builds,
    """

    boot_count_clause = """
    COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                    AND "status" = 'PASS' THEN 1 END) AS pass_boots,
    COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                    AND "status" = 'FAIL' THEN 1 END) AS fail_boots,
    SUM(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                    AND "status" IS NULL AND id IS NOT NULL THEN 1 ELSE 0 END) AS null_boots,
    COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                    AND "status" = 'ERROR' THEN 1 END) AS error_boots,
    COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                    AND "status" = 'MISS' THEN 1 END) AS miss_boots,
    COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                    AND "status" = 'DONE' THEN 1 END) AS done_boots,
    COUNT(CASE WHEN ("path" = 'boot' OR "path" LIKE 'boot.%%')
                    AND "status" = 'SKIP' THEN 1 END) AS skip_boots,
    """

    test_count_clause = """
    COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                    AND "status" = 'PASS' THEN 1 END) AS pass_tests,
    COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                    AND "status" = 'FAIL' THEN 1 END) AS fail_tests,
    SUM(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                    AND "status" IS NULL AND id IS NOT NULL THEN 1 ELSE 0 END) AS null_tests,
    COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                    AND "status" = 'ERROR' THEN 1 END) AS error_tests,
    COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                    AND "status" = 'MISS' THEN 1 END) AS miss_tests,
    COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                    AND "status" = 'DONE' THEN 1 END) AS done_tests,
    COUNT(CASE WHEN ("path" <> 'boot' AND "path" NOT LIKE 'boot.%%')
                    AND "status" = 'SKIP' THEN 1 END) AS skip_tests
    """

    return build_count_clause + boot_count_clause + test_count_clause


def get_hardware_listing_data(
    start_date: datetime, end_date: datetime, origin: str
) -> list[dict]:
    """
    Retrieves the listing of platform, compatibles, and
    the status counts of builds, boots and tests
    for the latest checkout of every tree.
    The selected checkouts and tests are limited to the start_date/end_date interval.
    """

    count_clauses = _get_hardware_listing_count_clauses()
    tree_head_clause = _get_hardware_tree_heads_clause(id_only=True)

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "origin": origin,
    }

    # The grouping by platform and compatibles is possible because a platform
    # can dictate the array of compatibles, meaning that if the array of compatibles
    # is different, then the platform should/must be different as well.
    #
    # It is possible that a platform appears for tests from origin A which are related
    # to checkouts from origin B. It's for those cases that the origin filter is applied
    # to the tests, not checkouts. There are no platforms being tested by multiple origins yet.
    query = f"""
        WITH
            -- Selects the id of the latest checkout of all trees in the given period.
            -- No checkout data is returned in the end.
            tree_heads AS (
                {tree_head_clause}
            ),
            -- Selects all tests/builds related to those checkouts.
            relevant_tests AS (
                SELECT
                    "tests"."environment_compatible" AS hardware,
                    "tests"."environment_misc" ->> 'platform' AS platform,
                    "tests"."status",
                    "tests"."path",
                    "tests"."id",
                    b.id AS build_id,
                    b.status AS build_status
                FROM
                    tests
                    INNER JOIN builds b ON tests.build_id = b.id
                    JOIN tree_heads TH ON b.checkout_id = TH.id
                WHERE
                    "tests"."environment_misc" ->> 'platform' IS NOT NULL
                    AND "tests"."origin" = %(origin)s
                    AND "tests"."start_time" >= %(start_date)s
                    AND "tests"."start_time" <= %(end_date)s
            )
        -- From the raw rows, selects platform, hardware, and performs the status grouping.
        SELECT
            platform,
            hardware,
            {count_clauses}
        FROM
            relevant_tests
        GROUP BY
            platform,
            hardware
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def get_hardware_listing_data_bulk(
    keys: list[tuple[str, str]],
    start_date: datetime,
    end_date: datetime,
    labs_by_key: dict[tuple[str, str], set[str]],
) -> list[dict]:
    if not keys:
        return []

    count_clauses = _get_hardware_listing_count_clauses()

    triples: list[tuple[str, str, str]] = []
    for hardware_id, origin in keys:
        lab_names = labs_by_key[(hardware_id, origin)]
        for lab in lab_names:
            triples.append((hardware_id, origin, lab))

    values_clause = ", ".join(
        [
            f"(%(hardware_id_{i})s, %(origin_{i})s, %(lab_name_{i})s)"
            for i in range(len(triples))
        ]
    )

    query = f"""
        WITH
            relevant_tests AS (
                SELECT
                    "tests"."environment_compatible" AS hardware,
                    "tests"."environment_misc" ->> 'platform' AS platform,
                    "tests"."status",
                    "tests"."path",
                    "tests"."origin" AS test_origin,
                    "tests"."id",
                    b.id AS build_id,
                    b.status AS build_status
                FROM
                    tests
                    INNER JOIN builds b ON tests.build_id = b.id
                WHERE
                    "tests"."environment_misc" ->> 'platform' IS NOT NULL
                    AND "tests"."start_time" >= %(start_date)s
                    AND "tests"."start_time" <= %(end_date)s
                    AND EXISTS (
                    SELECT 1
                    FROM (VALUES {values_clause}) AS key_list(hardware_id, origin, lab_name)
                    WHERE(
                        tests.environment_compatible @> ARRAY[key_list.hardware_id]::TEXT[]
                        OR tests.environment_misc ->> 'platform' = key_list.hardware_id
                    )
                    AND tests.origin = key_list.origin
                    AND tests.misc ->> 'runtime' = key_list.lab_name
                    )
            )
        SELECT
            platform,
            hardware,
            test_origin,
            {count_clauses}
        FROM
            relevant_tests
        GROUP BY
            platform,
            hardware,
            test_origin
    """

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }
    for i, (hardware_id, origin, lab_name) in enumerate(triples):
        params[f"hardware_id_{i}"] = hardware_id
        params[f"origin_{i}"] = origin
        params[f"lab_name_{i}"] = lab_name

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)


def get_hardware_listing_data_from_status_table(
    start_date: datetime, end_date: datetime, origin: str
) -> list[tuple]:
    """
    Retrieves hardware listing data from the HardwareStatus denormalized table.
    Groups by platform and compatibles, aggregating status counts.
    """
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "origin": origin,
    }

    query = """
        SELECT
            platform,
            compatibles AS hardware,
            SUM(build_pass) AS build_pass,
            SUM(build_failed) AS build_fail,
            SUM(build_inc) AS build_null,
            SUM(boot_pass) AS boot_pass,
            SUM(boot_failed) AS boot_fail,
            SUM(boot_inc) AS boot_null,
            SUM(test_pass) AS test_pass,
            SUM(test_failed) AS test_fail,
            SUM(test_inc) AS test_null
        FROM
            hardware_status
        INNER JOIN
            latest_checkout
            ON
                hardware_status.checkout_id = latest_checkout.checkout_id
            AND
                latest_checkout.start_time >= %(start_date)s
            AND
                latest_checkout.start_time <= %(end_date)s
        WHERE
            hardware_status.test_origin = %(origin)s
        GROUP BY
            platform,
            compatibles
        ORDER BY
            platform,
            compatibles
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def get_hardware_details_data(
    *,
    hardware_id: str,
    origin: str,
    trees_with_selected_commits: list[Tree],
    start_datetime: datetime,
    end_datetime: datetime,
):
    cache_key = "hardwareDetailsFullData"

    tests_cache_params = {
        "hardware_id": hardware_id,
        "origin": origin,
        "trees": trees_with_selected_commits,
        "start_date": start_datetime,
        "end_date": end_datetime,
    }

    records = get_query_cache(cache_key, tests_cache_params)

    if not records:
        records = query_records(
            hardware_id=hardware_id,
            origin=origin,
            trees=trees_with_selected_commits,
            start_date=start_datetime,
            end_date=end_datetime,
        )
        set_query_cache(key=cache_key, params=tests_cache_params, rows=records)

    return records


def query_records(
    *, hardware_id: str, origin: str, trees: list[Tree], start_date: int, end_date: int
) -> list[dict] | None:
    commit_hashes = [tree.head_git_commit_hash for tree in trees]

    # TODO Treat commit_hash collision (it can happen between repos)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                tests.id,
                tests.origin AS test_origin,
                tests.environment_misc,
                tests.path,
                tests.comment,
                tests.log_url,
                tests.status,
                tests.start_time,
                tests.duration,
                tests.misc,
                tests.build_id,
                tests.environment_compatible,
                builds.architecture AS build__architecture,
                builds.config_name AS build__config_name,
                builds.misc AS build__misc,
                builds.config_url AS build__config_url,
                builds.compiler AS build__compiler,
                builds.status AS build__status,
                builds.duration AS build__duration,
                builds.log_url AS build__log_url,
                builds.start_time AS build__start_time,
                builds.origin AS build__origin,
                checkouts.git_repository_url AS build__checkout__git_repository_url,
                checkouts.git_repository_branch AS build__checkout__git_repository_branch,
                checkouts.git_commit_name AS build__checkout__git_commit_name,
                checkouts.git_commit_hash AS build__checkout__git_commit_hash,
                checkouts.tree_name AS build__checkout__tree_name,
                checkouts.origin AS build__checkout__origin,
                incidents.id AS incidents__id,
                incidents.issue_id AS incidents__issue__id,
                issues.version AS incidents__issue__version,
                issues.comment AS incidents__issue__comment,
                issues.report_url AS incidents__issue__report_url,
                incidents.test_id AS incidents__test_id,
                T7.issue_id AS build__incidents__issue__id,
                T8.version AS build__incidents__issue__version
            FROM
                tests
            INNER JOIN builds ON
                tests.build_id = builds.id
            INNER JOIN checkouts ON
                builds.checkout_id = checkouts.id
            LEFT OUTER JOIN incidents ON
                tests.id = incidents.test_id
            LEFT OUTER JOIN issues ON
                incidents.issue_id = issues.id AND incidents.issue_version = issues.version
            LEFT OUTER JOIN incidents T7 ON
                builds.id = T7.build_id
            LEFT OUTER JOIN issues T8 ON
                T7.issue_id = T8.id AND T7.issue_version = T8.version
            WHERE
                (
                    tests.environment_compatible @> ARRAY[%s]::TEXT[]
                    OR tests.environment_misc ->> 'platform' = %s
                )
                AND tests.origin = %s
                AND tests.start_time >= %s
                AND tests.start_time <= %s
                AND checkouts.git_commit_hash IN ({0})
            ORDER BY
                issues."_timestamp" DESC
            """.format(
                ",".join(["%s"] * len(commit_hashes))
            ),
            [
                hardware_id,
                hardware_id,
                origin,
                start_date,
                end_date,
            ]
            + commit_hashes,
        )

        return dict_fetchall(cursor)


def get_hardware_summary_data(
    *,
    keys: list[tuple[str, str]],
    start_date: datetime,
    end_date: datetime,
    labs_by_key: dict[tuple[str, str], set[str]],
) -> list[dict] | None:
    """
    Get hardware summary data for given keys within a date range.
    Only failed tests are included in the result.
    """
    if not keys:
        return []

    triples: list[tuple[str, str, str]] = []
    for hardware_id, origin in keys:
        lab_names = labs_by_key[(hardware_id, origin)]
        for lab in lab_names:
            triples.append((hardware_id, origin, lab))

    with connection.cursor() as cursor:
        values_clause = ", ".join(["(%s, %s, %s)"] * len(triples))

        query = f"""
            SELECT
                tests.id,
                tests.origin AS test_origin,
                tests.environment_misc,
                tests.path,
                tests.comment,
                tests.log_url,
                tests.status,
                tests.start_time,
                tests.duration,
                tests.misc,
                tests.build_id,
                tests.environment_compatible,
                builds.architecture,
                builds.config_name,
                builds.misc AS build_misc,
                builds.config_url,
                builds.compiler,
                builds.status AS build_status,
                builds.duration AS build_duration,
                builds.log_url AS build_log_url,
                builds.start_time AS build_start_time,
                builds.origin AS build_origin,
                checkouts.git_repository_url,
                checkouts.git_repository_branch,
                checkouts.git_commit_name,
                checkouts.git_commit_hash,
                checkouts.tree_name,
                checkouts.origin AS checkout_origin
            FROM
                tests
            INNER JOIN builds ON
                tests.build_id = builds.id
            INNER JOIN checkouts ON
                builds.checkout_id = checkouts.id
            WHERE
                tests.start_time >= %s
                AND tests.start_time <= %s
                AND tests.status = 'FAIL'
                AND EXISTS (
                SELECT 1
                FROM (VALUES {values_clause}) AS key_list(hardware_id, origin, lab_name)
                WHERE(
                    tests.environment_compatible @> ARRAY[key_list.hardware_id]::TEXT[]
                    OR tests.environment_misc ->> 'platform' = key_list.hardware_id
                )
                AND tests.origin = key_list.origin
                AND tests.misc ->> 'runtime' = key_list.lab_name
                )
            ORDER BY
                tests.start_time DESC
            """

        params = [start_date, end_date]
        for hardware_id, origin, lab_name in triples:
            params.extend([hardware_id, origin, lab_name])

        cursor.execute(query, params)

        return dict_fetchall(cursor)


def get_hardware_trees_data(
    *,
    hardware_id: str,
    origin: str,
    start_datetime: datetime,
    end_datetime: datetime,
) -> list[Tree]:
    cache_key = "hardwareDetailsTreeData"

    params = {
        "hardware": hardware_id,
        "origin": origin,
        "start_date": start_datetime,
        "end_date": end_datetime,
    }

    trees: list[Tree] = get_query_cache(cache_key, params)

    tree_head_clause = _get_hardware_tree_heads_clause(id_only=False)

    if not trees:
        # We need a subquery because if we filter by any hardware, it will get the
        # last head that has that hardware, but not the real head of the trees
        query = f"""
        WITH
            -- Selects the data of the latest checkout of all trees in the given period
            tree_heads AS (
                {tree_head_clause}
            )
        SELECT DISTINCT
            ON (
                TH.tree_name,
                TH.git_repository_branch,
                TH.git_repository_url,
                TH.git_commit_hash
            ) TH.tree_name,
            TH.origin,
            TH.git_repository_branch,
            TH.git_repository_url,
            TH.git_commit_name,
            TH.git_commit_hash,
            TH.git_commit_tags
        FROM
            tests
            INNER JOIN builds ON tests.build_id = builds.id
            INNER JOIN tree_heads TH ON builds.checkout_id = TH.id
        WHERE
            (
                (
                    tests.environment_compatible @> ARRAY[%(hardware)s]::TEXT[]
                    OR tests.environment_misc ->> 'platform' = %(hardware)s
                )
                AND tests.origin = %(origin)s
                AND TH.start_time >= %(start_date)s
                AND TH.start_time <= %(end_date)s
            )
        ORDER BY
            TH.tree_name ASC,
            TH.git_repository_branch ASC,
            TH.git_repository_url ASC,
            TH.git_commit_hash ASC,
            TH.start_time DESC
        """
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            tree_records = dict_fetchall(cursor)

        trees = []
        for idx, tree in enumerate(tree_records):
            trees.append(
                Tree(
                    index=str(idx),
                    tree_name=tree["tree_name"],
                    origin=tree["origin"],
                    git_repository_branch=tree["git_repository_branch"],
                    git_repository_url=tree["git_repository_url"],
                    head_git_commit_name=tree["git_commit_name"],
                    head_git_commit_hash=tree["git_commit_hash"],
                    head_git_commit_tag=tree["git_commit_tags"],
                    selected_commit_status=None,
                    is_selected=None,
                )
            )

        set_query_cache(key=cache_key, params=params, rows=trees)

    return trees


class CommitHeadsQueryParams(TypedDict):
    query_params: dict[str, dict[str, str]]
    tuple_str: str


def _generate_query_params(
    commit_heads: list[CommitHead],
) -> CommitHeadsQueryParams:
    tuple_list = []
    params = {}

    for index, commit_head in enumerate(commit_heads):
        tree_name_key = f"tree_name{index}"
        git_repository_url_key = f"git_repository_url{index}"
        git_repository_branch_key = f"git_repository_branch{index}"
        git_commit_hash_key = f"git_commit_hash{index}"

        tuple_string = (
            f"(%({tree_name_key})s,"
            f"%({git_repository_url_key})s, %({git_repository_branch_key})s,"
            f"%({git_commit_hash_key})s)"
        )

        tuple_list.append(tuple_string)
        params[tree_name_key] = commit_head.treeName
        params[git_repository_url_key] = commit_head.repositoryUrl
        params[git_repository_branch_key] = commit_head.branch
        params[git_commit_hash_key] = commit_head.commitHash

    tuple_str = ", ".join(tuple_list)
    return {"tuple_str": f"({tuple_str})", "query_params": params}


def get_hardware_commit_history(
    *,
    origin: str,
    start_date: datetime,
    end_date: datetime,
    commit_heads: list[CommitHead],
):
    """Retrieves the history of commits for the trees that
    composes the hardware through a list of commit_heads.\n
    The history is limited by the origin, start_date and end dates params."""

    if not commit_heads:
        return

    commit_heads_params = _generate_query_params(commit_heads)

    params = {
        **commit_heads_params["query_params"],
        "origin": origin,
        "start_date": start_date,
        "end_date": end_date,
    }

    raw_query = f"""
        -- Selects the start_time of the latest checkout for the selected trees (+identifier fields)
        WITH filtered_checkouts AS (
            SELECT DISTINCT
                ON (
                    tree_name,
                    git_repository_url,
                    git_repository_branch,
                    origin
                )
                tree_name,
                git_repository_url,
                git_repository_branch,
                start_time
            FROM
                checkouts c
            WHERE
                (
                    c.tree_name,
                    c.git_repository_url,
                    c.git_repository_branch,
                    c.git_commit_hash
                ) IN {commit_heads_params['tuple_str']}
                AND c.origin = %(origin)s
            ORDER BY
                tree_name,
                git_repository_url,
                git_repository_branch,
                origin,
                c.start_time
        )
        -- Selects the data from all checkouts prior to the "head checkout" of
        -- the selected trees (while also limiting by the queried timestamps)
        SELECT
            fc.tree_name AS tree_name,
            fc.git_repository_url AS git_repository_url,
            fc.git_repository_branch AS git_repository_branch,
            lateralus.git_commit_tags AS git_commit_tags,
            lateralus.git_commit_name AS git_commit_name,
            lateralus.git_commit_hash AS git_commit_hash,
            lateralus.start_time AS start_time
        FROM
            filtered_checkouts fc,
            LATERAL (
                SELECT
                    DISTINCT ON (c.git_commit_hash)
                    c.git_commit_tags,
                    c.git_commit_name,
                    c.git_commit_hash,
                    c.start_time
                FROM
                    checkouts c
                WHERE
                    c.tree_name = fc.tree_name
                    AND c.git_repository_branch = fc.git_repository_branch
                    AND c.git_repository_url = fc.git_repository_url
                    AND c.start_time <= fc.start_time
                    AND c.start_time >= %(start_date)s
                    AND c.start_time <= %(end_date)s
                ORDER BY c.git_commit_hash, c.start_time
            ) AS lateralus;
        """

    with connection.cursor() as cursor:
        cursor.execute(raw_query, params)
        rows = cursor.fetchall()

    return rows
