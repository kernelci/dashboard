from datetime import datetime
from typing import Optional, TypedDict

from django.db import connection, connections

from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.constants.hardwareDetails import make_tree_key
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.models import HardwareRegistryPlatform
from kernelCI_app.queries.duration import (
    get_boot_test_duration_clause,
    get_build_duration_clause,
)
from kernelCI_app.typeModels.hardwareDetails import CommitHead, Tree


def _origin_clause(column: str, origins: list[str], param: str) -> tuple[str, dict]:
    """One origin stays an equality so the origin index can be used."""
    if len(origins) == 1:
        return f"{column} = %({param})s", {param: origins[0]}
    return f"{column} = ANY(%({param})s)", {param: origins}


def _and_origin_clause(
    column: str, origins: Optional[list[str]], param: str
) -> tuple[str, dict]:
    """Absent or empty means no predicate, the same rule as the hardware listing."""
    values = [origin for origin in (origins or []) if origin]
    if not values:
        return "", {}
    clause, params = _origin_clause(column, values, param)
    return f"AND {clause}", params


def _positional_origin_sql(
    column: str, origins: Optional[list[str]]
) -> tuple[str, list]:
    values = [origin for origin in (origins or []) if origin]
    if not values:
        return "", []
    if len(values) == 1:
        return f"AND {column} = %s", [values[0]]
    return f"AND {column} = ANY(%s)", [values]


def _get_hardware_trees_from_status_query(*, fields: str, checkout_clause: str) -> str:
    """Latest checkout per tree in the window for this hardware via hardware_status.

    Checkout origin is applied only when the listing selected one.
    """
    return f"""
        SELECT DISTINCT ON (
            C.tree_name,
            C.git_repository_branch,
            C.git_repository_url,
            C.origin
        )
            {fields}
        FROM
            hardware_status HS
            INNER JOIN checkouts C ON C.id = HS.checkout_id
        WHERE
            (
                HS.platform = %(hardware)s
                OR HS.compatibles @> ARRAY[%(hardware)s]::TEXT[]
            )
            {checkout_clause}
            AND HS.start_time >= %(start_date)s
            AND HS.start_time <= %(end_date)s
        ORDER BY
            C.tree_name ASC,
            C.git_repository_branch ASC,
            C.git_repository_url ASC,
            C.origin ASC,
            C.start_time DESC
    """


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


def get_hardware_selectors(build_origin: Optional[list[str]]) -> list[dict]:
    cache_key = "hardwareSelectors"
    cache_params = {"build_origin": build_origin}

    rows = get_query_cache(cache_key, cache_params)
    if rows is not None:
        return rows

    cross_origin_test_origins = {"aspeed", "ti"}

    if (
        build_origin
        and len(build_origin) == 1
        and build_origin[0] in cross_origin_test_origins
    ):
        params = {"origin": build_origin[0]}
        from_where = """
            FROM tests t
            INNER JOIN builds b ON b.id = t.build_id
            INNER JOIN checkouts c ON c.id = b.checkout_id
            WHERE
                t.origin = %(origin)s
                AND t.start_time > (NOW() - INTERVAL '30 days')
                AND t.environment_misc ->> 'platform' IS NOT NULL
        """
    else:
        params = {"build_origin": build_origin}
        build_origin_clause = (
            "AND b.origin = ANY(%(build_origin)s)" if build_origin else ""
        )
        from_where = f"""
            FROM checkouts c
            INNER JOIN builds b ON b.checkout_id = c.id
            WHERE
                b.start_time > (NOW() - INTERVAL '30 days')
                {build_origin_clause}
        """

    query = f"""
        SELECT DISTINCT ON (
            c.tree_name,
            c.git_repository_url,
            c.git_repository_branch,
            c.git_commit_hash,
            c.git_commit_name
        )
            c.tree_name,
            c.git_repository_url,
            c.git_repository_branch,
            c.git_commit_hash,
            c.git_commit_name,
            c.start_time
        {from_where}
            AND c.git_repository_url IS NOT NULL
            AND c.git_repository_branch IS NOT NULL
            AND c.git_commit_hash IS NOT NULL
            AND c.tree_name IS NOT NULL
        ORDER BY
            c.tree_name,
            c.git_repository_url,
            c.git_repository_branch,
            c.git_commit_hash,
            c.git_commit_name,
            c.start_time DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = dict_fetchall(cursor)

    set_query_cache(key=cache_key, params=cache_params, rows=rows, compress=True)
    return rows


def get_hardware_listing_data_by_revision(
    *,
    checkout_origin: Optional[list[str]],
    build_origin: Optional[list[str]],
    test_origin: Optional[list[str]],
    build_lab: Optional[list[str]],
    test_lab: Optional[list[str]],
    tree_name: str,
    git_repository_url: str,
    git_repository_branch: str,
    git_commit_hash: str,
) -> list[tuple]:
    checkouts = """
        SELECT id AS checkout_id
        FROM checkouts
        WHERE tree_name = %(tree_name)s
          AND git_repository_url = %(git_repository_url)s
          AND git_repository_branch = %(git_repository_branch)s
          AND git_commit_hash = %(git_commit_hash)s
    """

    return _hardware_daily_counts(
        checkouts=checkouts,
        day_range="",
        params={
            "tree_name": tree_name,
            "git_repository_url": git_repository_url,
            "git_repository_branch": git_repository_branch,
            "git_commit_hash": git_commit_hash,
        },
        checkout_origin=checkout_origin,
        build_origin=build_origin,
        test_origin=test_origin,
        build_lab=build_lab,
        test_lab=test_lab,
    )


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
                    LEFT JOIN labs tl ON tests.lab_id = tl.id
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
                    -- TODO remove misc->>'runtime' fallback after lab backfill
                    AND COALESCE(tl.name, tests.misc ->> 'runtime') = key_list.lab_name
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


def _hardware_filter_clause(
    column: str, parameter: str, values: Optional[list[str]]
) -> str:
    return f"AND {column} = ANY(%({parameter})s)" if values else ""


def _daily_aggregate_rows(table: str, checkouts: Optional[str], filters: str) -> str:
    if checkouts is not None:
        return f"""
            SELECT daily.*
            FROM {table} daily
            INNER JOIN selected_checkouts selected
                ON selected.checkout_id = daily.checkout_id
                {filters}"""

    predicates = [
        line.strip().removeprefix("AND ")
        for line in filters.splitlines()
        if line.strip()
    ]
    if not predicates:
        return f"""
            SELECT daily.*
            FROM {table} daily"""

    return f"""
            SELECT daily.*
            FROM {table} daily
            WHERE {" AND ".join(predicates)}"""


def _platform_counts_cte(*, rows: str, prefix: str, sums: str) -> str:
    return f"""
        {prefix}_hardware AS (
            SELECT DISTINCT ON (platform) platform, compatibles
            FROM {rows}
            WHERE compatibles IS NOT NULL
            ORDER BY platform, CARDINALITY(compatibles) DESC, compatibles
        ),
        {prefix}_counts AS (
            SELECT
                daily.platform,
                hardware.compatibles AS hardware,
                {sums}
            FROM {rows} daily
            LEFT JOIN {prefix}_hardware hardware USING (platform)
            GROUP BY daily.platform, hardware.compatibles
        )"""


def _hardware_daily_counts(
    *,
    checkouts: Optional[str],
    day_range: str,
    params: dict,
    checkout_origin: Optional[list[str]],
    build_origin: Optional[list[str]],
    test_origin: Optional[list[str]],
    build_lab: Optional[list[str]],
    test_lab: Optional[list[str]],
) -> list[tuple]:
    """Counts from daily aggregates. Build/test filtered independently; narrowed side picks platforms.
    Optional checkouts narrows checkout_id; else checkout_day window only."""
    # checkout_origin is nullable: rows whose checkout has been pruned, and rows
    # aggregated before the column existed, have no origin to compare. Narrowing
    # to an origin leaves them out rather than matching them against every one.
    checkout_origin_clause = _hardware_filter_clause(
        "daily.checkout_origin", "checkout_origin", checkout_origin
    )
    build_filters = "\n".join(
        (
            day_range,
            checkout_origin_clause,
            _hardware_filter_clause("daily.build_origin", "build_origin", build_origin),
            _hardware_filter_clause("daily.build_lab", "build_lab", build_lab),
        )
    )
    test_filters = "\n".join(
        (
            day_range,
            checkout_origin_clause,
            _hardware_filter_clause("daily.test_origin", "test_origin", test_origin),
            _hardware_filter_clause("daily.test_lab", "test_lab", test_lab),
        )
    )
    sides_join = {
        (True, True): "INNER JOIN",
        (True, False): "LEFT JOIN",
        (False, True): "RIGHT JOIN",
        (False, False): "FULL OUTER JOIN",
    }[bool(build_origin or build_lab), bool(test_origin or test_lab)]

    scope_cte = f"selected_checkouts AS ({checkouts}),\n        " if checkouts else ""

    query = f"""
        WITH {scope_cte}build_rows AS (
        {_daily_aggregate_rows("hardware_daily_builds", checkouts, build_filters)}
        ),
        {
        _platform_counts_cte(
            rows="build_rows",
            prefix="build",
            sums='''
                SUM(daily.build_pass) AS build_pass,
                SUM(daily.build_failed) AS build_failed,
                SUM(daily.build_inc) AS build_inc''',
        )
    },
        test_rows AS (
        {_daily_aggregate_rows("hardware_daily_tests", checkouts, test_filters)}
        ),
        {
        _platform_counts_cte(
            rows="test_rows",
            prefix="test",
            sums='''
                SUM(daily.boot_pass) AS boot_pass,
                SUM(daily.boot_failed) AS boot_failed,
                SUM(daily.boot_inc) AS boot_inc,
                SUM(daily.test_pass) AS test_pass,
                SUM(daily.test_failed) AS test_failed,
                SUM(daily.test_inc) AS test_inc''',
        )
    }
        SELECT
            COALESCE(builds.platform, tests.platform) AS platform,
            COALESCE(tests.hardware, builds.hardware) AS hardware,
            COALESCE(builds.build_pass, 0),
            COALESCE(builds.build_failed, 0),
            COALESCE(builds.build_inc, 0),
            COALESCE(tests.boot_pass, 0),
            COALESCE(tests.boot_failed, 0),
            COALESCE(tests.boot_inc, 0),
            COALESCE(tests.test_pass, 0),
            COALESCE(tests.test_failed, 0),
            COALESCE(tests.test_inc, 0)
        FROM build_counts builds
        {sides_join} test_counts tests ON tests.platform = builds.platform
        ORDER BY platform
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            {
                **params,
                "checkout_origin": checkout_origin,
                "build_origin": build_origin,
                "test_origin": test_origin,
                "build_lab": build_lab,
                "test_lab": test_lab,
            },
        )
        return cursor.fetchall()


def get_hardware_listing_data(
    *,
    start_date: datetime,
    end_date: datetime,
    checkout_origin: Optional[list[str]],
    build_origin: Optional[list[str]],
    test_origin: Optional[list[str]],
    build_lab: Optional[list[str]],
    test_lab: Optional[list[str]],
    commits_list: Optional[list[str]] = None,
) -> list[tuple]:
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "start_day": start_date.date(),
        "end_day": end_date.date(),
    }

    if commits_list:
        params["commits_list"] = commits_list
        checkouts = """
            SELECT id AS checkout_id
            FROM checkouts
            WHERE start_time >= %(start_date)s
              AND start_time <= %(end_date)s
              AND (
                  git_commit_hash = ANY(%(commits_list)s)
                  OR git_commit_tags && %(commits_list)s::text[]
              )
        """
    else:
        checkouts = None

    return _hardware_daily_counts(
        checkouts=checkouts,
        day_range="AND daily.checkout_day BETWEEN %(start_day)s AND %(end_day)s",
        params=params,
        checkout_origin=checkout_origin,
        build_origin=build_origin,
        test_origin=test_origin,
        build_lab=build_lab,
        test_lab=test_lab,
    )


def get_hardware_filters(
    *, start_date: datetime, end_date: datetime
) -> dict[str, list[str]]:
    """Filter option lists for the listing window. Lists are independent (no cascading)."""
    cache_key = "hardwareFilters"
    cache_params = {"start_date": start_date, "end_date": end_date}

    cached = get_query_cache(cache_key, cache_params)
    if cached is not None:
        return cached[0]

    query = """
        WITH days AS (
            SELECT %(start_day)s::date AS start_day, %(end_day)s::date AS end_day
        )
        SELECT
            ARRAY(
                SELECT DISTINCT origin FROM (
                    SELECT checkout_origin AS origin
                    FROM hardware_daily_builds, days
                    WHERE checkout_day BETWEEN start_day AND end_day
                    UNION
                    SELECT checkout_origin AS origin
                    FROM hardware_daily_tests, days
                    WHERE checkout_day BETWEEN start_day AND end_day
                ) checkout_origins
                WHERE origin IS NOT NULL AND origin <> ''
                ORDER BY origin
            ),
            ARRAY(
                SELECT DISTINCT build_origin
                FROM hardware_daily_builds, days
                WHERE checkout_day BETWEEN start_day AND end_day
                  AND build_origin <> ''
                ORDER BY build_origin
            ),
            ARRAY(
                SELECT DISTINCT test_origin
                FROM hardware_daily_tests, days
                WHERE checkout_day BETWEEN start_day AND end_day
                  AND test_origin <> ''
                ORDER BY test_origin
            ),
            ARRAY(
                SELECT DISTINCT build_lab
                FROM hardware_daily_builds, days
                WHERE checkout_day BETWEEN start_day AND end_day
                  AND build_lab <> ''
                ORDER BY build_lab
            ),
            ARRAY(
                SELECT DISTINCT test_lab
                FROM hardware_daily_tests, days
                WHERE checkout_day BETWEEN start_day AND end_day
                  AND test_lab <> ''
                ORDER BY test_lab
            )
    """
    with connection.cursor() as cursor:
        cursor.execute(
            query, {"start_day": start_date.date(), "end_day": end_date.date()}
        )
        row = cursor.fetchone()

    filters = {
        "checkout_origins": row[0],
        "build_origins": row[1],
        "test_origins": row[2],
        "build_labs": row[3],
        "test_labs": row[4],
    }
    set_query_cache(key=cache_key, params=cache_params, rows=[filters])
    return filters


def get_hardware_details_data(
    *,
    hardware_id: str,
    trees_with_selected_commits: list[Tree],
    start_datetime: datetime,
    end_datetime: datetime,
    test_origins: Optional[list[str]] = None,
):
    cache_key = "hardwareDetailsFullDataByCheckout"

    tests_cache_params = {
        "hardware_id": hardware_id,
        "test_origins": test_origins,
        "trees": trees_with_selected_commits,
        "start_date": start_datetime,
        "end_date": end_datetime,
    }

    records = get_query_cache(cache_key, tests_cache_params)

    if not records:
        records = query_records(
            hardware_id=hardware_id,
            test_origins=test_origins,
            trees=trees_with_selected_commits,
            start_date=start_datetime,
            end_date=end_datetime,
        )
        set_query_cache(
            key=cache_key, params=tests_cache_params, rows=records, compress=True
        )

    return records


def get_hardware_build_data(
    *,
    hardware_id: str,
    trees_with_selected_commits: list[Tree],
    start_datetime: datetime,
    end_datetime: datetime,
    build_origins: Optional[list[str]] = None,
):
    cache_key = "hardwareDetailsBuildDataByCheckout"
    cache_params = {
        "hardware_id": hardware_id,
        "build_origins": build_origins,
        "trees": trees_with_selected_commits,
        "start_date": start_datetime,
        "end_date": end_datetime,
    }
    records = get_query_cache(cache_key, cache_params)
    if not records:
        records = query_build_records(
            hardware_id=hardware_id,
            trees=trees_with_selected_commits,
            start_date=start_datetime,
            end_date=end_datetime,
            build_origins=build_origins,
        )
        set_query_cache(key=cache_key, params=cache_params, rows=records)
    return records


def _checkout_commit_values(
    checkouts: list[tuple[str, str, str, str, str]],
) -> tuple[str, dict[str, str]]:
    """Hash and origin still match another tree that checked out the same commit."""
    tuples = []
    params = {}

    for index, (tree_name, url, branch, commit_hash, checkout_origin) in enumerate(
        checkouts
    ):
        name_key = f"tree_name{index}"
        url_key = f"git_repository_url{index}"
        branch_key = f"git_repository_branch{index}"
        hash_key = f"commit_hash{index}"
        origin_key = f"checkout_origin{index}"
        tuples.append(
            f"(%({name_key})s, %({url_key})s, %({branch_key})s,"
            f" %({hash_key})s, %({origin_key})s)"
        )
        params[name_key] = tree_name
        params[url_key] = url
        params[branch_key] = branch
        params[hash_key] = commit_hash
        params[origin_key] = checkout_origin

    return ", ".join(tuples), params


def get_hardware_details_summary(
    *,
    hardware_id: str,
    checkouts: list[tuple[str, str, str, str, str]],
    builds_duration: Optional[tuple[Optional[int], Optional[int]]] = None,
    boots_duration: Optional[tuple[Optional[int], Optional[int]]] = None,
    tests_duration: Optional[tuple[Optional[int], Optional[int]]] = None,
    start_datetime: datetime,
    end_datetime: datetime,
    test_origins: Optional[list[str]] = None,
    build_origins: Optional[list[str]] = None,
):
    if not checkouts:
        return []

    if builds_duration is None:
        builds_duration = (None, None)
    if boots_duration is None:
        boots_duration = (None, None)
    if tests_duration is None:
        tests_duration = (None, None)

    cache_key = "hardwareDetailsSummaryByCheckout"

    tests_cache_params = {
        "hardware_id": hardware_id,
        "test_origins": test_origins,
        "build_origins": build_origins,
        "checkouts": checkouts,
        "start_date": start_datetime.timestamp(),
        "end_date": end_datetime.timestamp(),
        "builds_duration": builds_duration,
        "boots_duration": boots_duration,
        "tests_duration": tests_duration,
    }

    query_rows = get_query_cache(cache_key, tests_cache_params)

    if query_rows is not None:
        return query_rows

    checkout_clause, checkout_params = _checkout_commit_values(checkouts)
    test_origin_clause, test_origin_params = _and_origin_clause(
        "tests.origin", test_origins, "test_origins"
    )
    build_origin_clause, build_origin_params = _and_origin_clause(
        "builds.origin", build_origins, "build_origins"
    )
    platform_predicate = """(
                    tests.environment_misc ->> 'platform' = %(platform)s
                    OR tests.environment_compatible @> ARRAY[%(platform)s]::TEXT[]
                )"""

    query = """
           (SELECT
                 COUNT(DISTINCT builds.id) AS count,
                 checkouts.origin,
                 builds.status AS status,
                 count(DISTINCT incidents.id) AS incidents_count,
                 array_agg(DISTINCT incidents.issue_id || ',' || incidents.issue_version::text)
                     AS known_issues,
                 array[builds.compiler, builds.architecture] AS compiler_arch,
                 builds.config_name,
                 -- TODO remove misc->>'lab' fallback after lab backfill
                 COALESCE(bl.name, builds.misc->>'lab') AS lab,
                 tests.environment_misc->>'platform' AS platform,
                 tests.environment_compatible,
                 checkouts.tree_name,
                 checkouts.git_repository_url,
                 checkouts.git_commit_tags,
                 checkouts.git_commit_name,
                 checkouts.git_repository_branch,
                 checkouts.git_commit_hash,
                 true AS is_build,
                 false AS is_test,
                 false AS is_boot
             FROM
                checkouts
            INNER JOIN builds ON
                builds.checkout_id = checkouts.id
            INNER JOIN tests ON
                tests.build_id = builds.id
            LEFT JOIN labs bl ON builds.lab_id = bl.id
            LEFT OUTER JOIN incidents ON
                builds.id = incidents.build_id
            WHERE
                builds.config_name IS NOT NULL
                AND builds.id not like 'maestro:dummy_%%'
                {build_origin_clause}
                AND builds.start_time >= %(start_date)s
                AND builds.start_time <= %(end_date)s
                AND tests.start_time >= %(start_date)s
                AND tests.start_time <= %(end_date)s
                AND {platform_predicate}
                AND (
                    checkouts.tree_name,
                    checkouts.git_repository_url,
                    checkouts.git_repository_branch,
                    checkouts.git_commit_hash,
                    checkouts.origin
                ) IN (VALUES {checkout_values}) {builds_duration_clause}
            GROUP BY checkouts.id, builds.status, tests.environment_compatible, compiler_arch,
                builds.config_name, lab, platform, is_boot)
            UNION ALL
            (SELECT
                 COUNT(*) AS count,
                 checkouts.origin,
                 tests.status AS status,
                 count(DISTINCT incidents.id) as incidents_count,
                 array_agg(DISTINCT incidents.issue_id || ',' || incidents.issue_version::text)
                     as known_issues,
                 array[builds.compiler, builds.architecture] AS compiler_arch,
                 builds.config_name,
                 -- TODO remove misc->>'runtime' fallback after lab backfill
                 COALESCE(tl.name, tests.misc->>'runtime') AS lab,
                 tests.environment_misc->>'platform' AS platform,
                 tests.environment_compatible,
                 checkouts.tree_name,
                 checkouts.git_repository_url,
                 checkouts.git_commit_tags,
                 checkouts.git_commit_name,
                 checkouts.git_repository_branch,
                 checkouts.git_commit_hash,
                 false AS is_build,
                 true AS is_test,
                 (tests.path like 'boot.%%' or tests.path = 'boot') AS is_boot
             FROM
                checkouts
            INNER JOIN builds ON
                builds.checkout_id = checkouts.id
            INNER JOIN tests ON
                tests.build_id = builds.id
            LEFT JOIN labs tl ON tests.lab_id = tl.id
            LEFT OUTER JOIN incidents ON
                tests.id = incidents.test_id
            WHERE
                tests.start_time >= %(start_date)s
                AND tests.start_time <= %(end_date)s
                AND {platform_predicate}
                {test_origin_clause}
                AND (
                    checkouts.tree_name,
                    checkouts.git_repository_url,
                    checkouts.git_repository_branch,
                    checkouts.git_commit_hash,
                    checkouts.origin
                ) IN (VALUES {checkout_values}) {boots_tests_duration_clause}
            GROUP BY checkouts.id, tests.status, tests.environment_compatible, compiler_arch,
                builds.config_name, lab, platform, is_boot);
    """.format(
        builds_duration_clause=get_build_duration_clause(builds_duration),
        boots_tests_duration_clause=get_boot_test_duration_clause(
            boots_duration, tests_duration
        ),
        checkout_values=checkout_clause,
        test_origin_clause=test_origin_clause,
        build_origin_clause=build_origin_clause,
        platform_predicate=platform_predicate,
    )

    build_duration_min, build_duration_max = builds_duration
    boot_duration_min, boot_duration_max = boots_duration
    test_duration_min, test_duration_max = tests_duration

    params = {
        "platform": hardware_id,
        "start_date": start_datetime,
        "end_date": end_datetime,
        **test_origin_params,
        **build_origin_params,
        **checkout_params,
        "build_duration_min": build_duration_min,
        "build_duration_max": build_duration_max,
        "boot_duration_min": boot_duration_min,
        "boot_duration_max": boot_duration_max,
        "test_duration_min": test_duration_min,
        "test_duration_max": test_duration_max,
    }

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        query_rows = dict_fetchall(cursor)
        set_query_cache(
            key=cache_key, params=tests_cache_params, rows=query_rows, compress=True
        )
        return query_rows


def _checkout_rows(trees: list[Tree]) -> list[tuple]:
    return [
        (
            tree.tree_name or "",
            tree.git_repository_url or "",
            tree.git_repository_branch or "",
            tree.head_git_commit_hash,
            tree.origin or "",
        )
        for tree in trees
        if tree.head_git_commit_hash
    ]


def query_records(
    *,
    hardware_id: str,
    trees: list[Tree],
    start_date: int,
    end_date: int,
    test_origins: Optional[list[str]] = None,
) -> list[dict] | None:
    checkouts = _checkout_rows(trees)
    if not checkouts:
        return []

    test_origin_sql, test_origin_params = _positional_origin_sql(
        "tests.origin", test_origins
    )

    query = """
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
                T8.version AS build__incidents__issue__version,
                -- TODO remove misc->>'runtime' fallback after lab backfill
                COALESCE(tl.name, tests.misc->>'runtime') AS lab,
                -- TODO remove misc->>'lab' fallback after lab backfill
                COALESCE(bl.name, builds.misc->>'lab') AS build_lab
            FROM
                tests
            INNER JOIN builds ON
                tests.build_id = builds.id
            INNER JOIN checkouts ON
                builds.checkout_id = checkouts.id
            LEFT JOIN labs tl ON
                tests.lab_id = tl.id
            LEFT JOIN labs bl ON
                builds.lab_id = bl.id
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
                {test_origin_sql}
                AND tests.start_time >= %s
                AND tests.start_time <= %s
                AND (
                    checkouts.tree_name,
                    checkouts.git_repository_url,
                    checkouts.git_repository_branch,
                    checkouts.git_commit_hash,
                    checkouts.origin
                ) IN ({checkouts})
            ORDER BY
                issues."_timestamp" DESC
            """.format(
        test_origin_sql=test_origin_sql,
        checkouts=", ".join(["(%s, %s, %s, %s, %s)"] * len(checkouts)),
    )

    params = [
        hardware_id,
        hardware_id,
        *test_origin_params,
        start_date,
        end_date,
    ] + [value for checkout in checkouts for value in checkout]

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        query_rows = dict_fetchall(cursor)
        return query_rows


def query_build_records(
    *,
    hardware_id: str,
    trees: list[Tree],
    start_date: datetime,
    end_date: datetime,
    build_origins: Optional[list[str]] = None,
) -> list[dict] | None:
    """One row per build on the selected checkouts that tested this platform."""
    checkouts = _checkout_rows(trees)
    if not checkouts:
        return []

    build_origin_sql, build_origin_params = _positional_origin_sql(
        "builds.origin", build_origins
    )
    query = """
            SELECT DISTINCT ON (builds.id)
                builds.status AS status,
                NULL::text AS path,
                builds.id AS id,
                tests.origin AS test_origin,
                tests.environment_misc,
                NULL::text AS comment,
                NULL::text AS log_url,
                tests.start_time,
                tests.duration,
                tests.misc,
                builds.id AS build_id,
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
                NULL::text AS incidents__id,
                NULL::text AS incidents__issue__id,
                NULL::integer AS incidents__issue__version,
                NULL::text AS incidents__issue__comment,
                NULL::text AS incidents__issue__report_url,
                NULL::text AS incidents__test_id,
                T7.issue_id AS build__incidents__issue__id,
                T8.version AS build__incidents__issue__version,
                NULL::text AS lab,
                COALESCE(bl.name, builds.misc->>'lab') AS build_lab
            FROM
                checkouts
            INNER JOIN builds ON
                builds.checkout_id = checkouts.id
            INNER JOIN tests ON
                tests.build_id = builds.id
            LEFT JOIN labs bl ON
                builds.lab_id = bl.id
            LEFT OUTER JOIN incidents T7 ON
                builds.id = T7.build_id
            LEFT OUTER JOIN issues T8 ON
                T7.issue_id = T8.id AND T7.issue_version = T8.version
            WHERE
                (
                    tests.environment_misc ->> 'platform' = %s
                    OR tests.environment_compatible @> ARRAY[%s]::TEXT[]
                )
                {build_origin_sql}
                AND builds.start_time >= %s
                AND builds.start_time <= %s
                AND tests.start_time >= %s
                AND tests.start_time <= %s
                AND builds.config_name IS NOT NULL
                AND builds.id NOT LIKE 'maestro:dummy_%%'
                AND (
                    checkouts.tree_name,
                    checkouts.git_repository_url,
                    checkouts.git_repository_branch,
                    checkouts.git_commit_hash,
                    checkouts.origin
                ) IN ({checkouts})
            ORDER BY
                builds.id, tests.start_time DESC
            """.format(
        build_origin_sql=build_origin_sql,
        checkouts=", ".join(["(%s, %s, %s, %s, %s)"] * len(checkouts)),
    )
    params = [
        hardware_id,
        hardware_id,
        *build_origin_params,
        start_date,
        end_date,
        start_date,
        end_date,
    ] + [value for checkout in checkouts for value in checkout]
    with connection.cursor() as cursor:
        cursor.execute(query, params)
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
                checkouts.origin AS checkout_origin,
                -- TODO remove misc->>'runtime' fallback after lab backfill
                COALESCE(tl.name, tests.misc->>'runtime') AS lab
            FROM
                tests
            INNER JOIN builds ON
                tests.build_id = builds.id
            INNER JOIN checkouts ON
                builds.checkout_id = checkouts.id
            LEFT JOIN labs tl ON tests.lab_id = tl.id
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
                -- TODO remove misc->>'runtime' fallback after lab backfill
                AND COALESCE(tl.name, tests.misc ->> 'runtime') = key_list.lab_name
                )
            ORDER BY
                tests.start_time DESC
            """

        params = [start_date, end_date]
        for hardware_id, origin, lab_name in triples:
            params.extend([hardware_id, origin, lab_name])

        cursor.execute(query, params)

        return dict_fetchall(cursor)


def get_hardware_trees_head_commits(
    *,
    hardware_id: str,
    start_datetime: datetime,
    end_datetime: datetime,
    checkout_origins: Optional[list[str]] = None,
) -> list[tuple[str, str, str, str, str, str]]:
    cache_key = "hardwareTreesHeadCommitsByCheckout"

    cache_params = {
        "hardware": hardware_id,
        "checkout_origins": checkout_origins,
        "start_date": start_datetime.timestamp(),
        "end_date": end_datetime.timestamp(),
    }

    trees: list[tuple[str, str, str, str, str, str]] = get_query_cache(
        cache_key, cache_params
    )

    if trees:
        return trees

    checkout_clause, origin_params = _and_origin_clause(
        "C.origin", checkout_origins, "checkout_origins"
    )
    query = _get_hardware_trees_from_status_query(
        fields="""
            C.tree_name,
            C.git_repository_branch,
            C.git_repository_url,
            C.origin,
            C.git_commit_hash
        """,
        checkout_clause=checkout_clause,
    )

    params = {
        "hardware": hardware_id,
        "start_date": start_datetime,
        "end_date": end_datetime,
        **origin_params,
    }
    with connections["default"].cursor() as cursor:
        cursor.execute(query, params)
        tree_records = dict_fetchall(cursor)
        trees = [
            (
                make_tree_key(
                    tree["tree_name"] or "",
                    tree["git_repository_branch"] or "",
                    tree["git_repository_url"] or "",
                    tree["origin"] or "",
                ),
                tree["tree_name"] or "",
                tree["git_repository_url"] or "",
                tree["git_repository_branch"] or "",
                tree["git_commit_hash"],
                tree["origin"] or "",
            )
            for tree in tree_records
        ]
        set_query_cache(key=cache_key, params=cache_params, rows=trees)

    return trees


def get_hardware_trees_data(
    *,
    hardware_id: str,
    start_datetime: datetime,
    end_datetime: datetime,
    checkout_origins: Optional[list[str]] = None,
) -> list[Tree]:
    cache_key = "hardwareDetailsTreeDataByTreeKey"

    cache_params = {
        "hardware": hardware_id,
        "checkout_origins": checkout_origins,
        "start_date": start_datetime,
        "end_date": end_datetime,
    }

    trees: list[Tree] = get_query_cache(cache_key, cache_params)

    if not trees:
        checkout_clause, origin_params = _and_origin_clause(
            "C.origin", checkout_origins, "checkout_origins"
        )
        query = _get_hardware_trees_from_status_query(
            fields="""
                C.tree_name,
                C.origin,
                C.git_repository_branch,
                C.git_repository_url,
                C.git_commit_name,
                C.git_commit_hash,
                C.git_commit_tags
            """,
            checkout_clause=checkout_clause,
        )
        with connections["default"].cursor() as cursor:
            cursor.execute(
                query,
                {
                    "hardware": hardware_id,
                    "start_date": start_datetime,
                    "end_date": end_datetime,
                    **origin_params,
                },
            )
            tree_records = dict_fetchall(cursor)

        trees = []
        for tree in tree_records:
            tree_index = make_tree_key(
                tree["tree_name"] or "",
                tree["git_repository_branch"] or "",
                tree["git_repository_url"] or "",
                tree["origin"] or "",
            )
            trees.append(
                Tree(
                    index=tree_index,
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

        set_query_cache(key=cache_key, params=cache_params, rows=trees, compress=True)

    return trees


class CommitHeadsQueryParams(TypedDict):
    query_params: dict[str, dict[str, str]]
    tuple_str: str


def _generate_query_params(
    commit_heads: list[CommitHead],
    *,
    default_origin: str,
) -> CommitHeadsQueryParams:
    tuple_list = []
    params = {}

    for index, commit_head in enumerate(commit_heads):
        tree_name_key = f"tree_name{index}"
        git_repository_url_key = f"git_repository_url{index}"
        git_repository_branch_key = f"git_repository_branch{index}"
        git_commit_hash_key = f"git_commit_hash{index}"
        checkout_origin_key = f"checkout_origin{index}"

        tuple_string = (
            f"(%({tree_name_key})s,"
            f"%({git_repository_url_key})s, %({git_repository_branch_key})s,"
            f"%({git_commit_hash_key})s, %({checkout_origin_key})s)"
        )

        tuple_list.append(tuple_string)
        params[tree_name_key] = commit_head.treeName
        params[git_repository_url_key] = commit_head.repositoryUrl
        params[git_repository_branch_key] = commit_head.branch
        params[git_commit_hash_key] = commit_head.commitHash
        params[checkout_origin_key] = commit_head.origin or default_origin

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
    Each head is limited to its checkout origin. Heads without one use origin."""

    if not commit_heads:
        return

    commit_heads_params = _generate_query_params(commit_heads, default_origin=origin)

    params = {
        **commit_heads_params["query_params"],
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
                origin,
                start_time
            FROM
                checkouts c
            WHERE
                (
                    c.tree_name,
                    c.git_repository_url,
                    c.git_repository_branch,
                    c.git_commit_hash,
                    c.origin
                ) IN {commit_heads_params["tuple_str"]}
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
            lateralus.start_time AS start_time,
            fc.origin AS origin
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
                    AND c.origin = fc.origin
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


def is_hardware_in_registry(hardware_id: str) -> bool:
    return HardwareRegistryPlatform.objects.filter(pk=hardware_id).exists()
