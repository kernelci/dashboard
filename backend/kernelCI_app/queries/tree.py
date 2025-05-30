from typing import Optional
from django.db import connection
from django.db.utils import ProgrammingError

from kernelCI_app.helpers.environment import (
    DEFAULT_SCHEMA_VERSION,
    get_schema_version,
    set_schema_version,
)
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.models import Checkouts
from kernelCI_app.utils import get_query_time_interval
from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.helpers.treeDetails import create_checkouts_where_clauses
from kernelCI_app.helpers.build import (
    is_valid_does_not_exist_exception,
    valid_status_field,
)
from kernelCI_app.helpers.logger import log_message


def _get_tree_listing_count_clause() -> str:
    build_valid_count_clause = """
        COUNT(DISTINCT CASE WHEN (builds.valid = true AND builds.id NOT LIKE 'maestro:dummy_%%')
            THEN builds.id END) AS pass_builds,
        COUNT(DISTINCT CASE WHEN (builds.valid = false AND builds.id NOT LIKE 'maestro:dummy_%%')
            THEN builds.id END) AS fail_builds,
        COUNT(DISTINCT CASE WHEN (builds.valid IS NULL AND builds.id IS NOT NULL
            AND builds.id NOT LIKE 'maestro:dummy_%%') THEN builds.id END) AS null_builds,
        0 AS error_builds,
        0 AS miss_builds,
        0 AS done_builds,
        0 AS skip_builds,
    """

    build_status_count_clause = """
        COUNT(DISTINCT CASE WHEN (builds.status = 'PASS' AND builds.id NOT LIKE 'maestro:dummy_%%')
            THEN builds.id END) AS pass_builds,
        COUNT(DISTINCT CASE WHEN (builds.status = 'FAIL' AND builds.id NOT LIKE 'maestro:dummy_%%')
            THEN builds.id END) AS fail_builds,
        COUNT(DISTINCT CASE WHEN (builds.status IS NULL AND builds.id IS NOT NULL
            AND builds.id NOT LIKE 'maestro:dummy_%%') THEN builds.id END) AS null_builds,
        COUNT(DISTINCT CASE WHEN (builds.status = 'ERROR' AND builds.id NOT LIKE 'maestro:dummy_%%')
            THEN builds.id END) AS error_builds,
        COUNT(DISTINCT CASE WHEN (builds.status = 'MISS' AND builds.id NOT LIKE 'maestro:dummy_%%')
            THEN builds.id END) AS miss_builds,
        COUNT(DISTINCT CASE WHEN (builds.status = 'DONE' AND builds.id NOT LIKE 'maestro:dummy_%%')
            THEN builds.id END) AS done_builds,
        COUNT(DISTINCT CASE WHEN (builds.status = 'SKIP' AND builds.id NOT LIKE 'maestro:dummy_%%')
            THEN builds.id END) AS skip_builds,
    """

    build_count_clause = (
        build_valid_count_clause
        if get_schema_version() == "4"
        else build_status_count_clause
    )

    test_count_clause = """
        COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
            AND tests.status = 'FAIL' THEN 1 END) AS fail_tests,
        COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
            AND tests.status = 'ERROR' THEN 1 END) AS error_tests,
        COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
            AND tests.status = 'MISS' THEN 1 END) AS miss_tests,
        COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
            AND tests.status = 'PASS' THEN 1 END) AS pass_tests,
        COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
            AND tests.status = 'DONE' THEN 1 END) AS done_tests,
        COUNT(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
            AND tests.status = 'SKIP' THEN 1 END) AS skip_tests,
        SUM(CASE WHEN (tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%')
            AND tests.status IS NULL AND tests.id IS NOT NULL THEN 1 ELSE 0 END) AS null_tests,
    """

    boot_count_clause = """
        COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
            AND tests.status = 'FAIL' THEN 1 END) AS fail_boots,
        COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
            AND tests.status = 'ERROR' THEN 1 END) AS error_boots,
        COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
            AND tests.status = 'MISS' THEN 1 END) AS miss_boots,
        COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
            AND tests.status = 'PASS' THEN 1 END) AS pass_boots,
        COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
            AND tests.status = 'DONE' THEN 1 END) AS done_boots,
        COUNT(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
            AND tests.status = 'SKIP' THEN 1 END) AS skip_boots,
        SUM(CASE WHEN (tests.path = 'boot' OR tests.path LIKE 'boot.%%')
            AND tests.status IS NULL AND tests.id IS NOT NULL THEN 1 ELSE 0 END) AS null_boots,
    """

    return build_count_clause + test_count_clause + boot_count_clause


def get_tree_listing_query(with_clause, join_clause, where_clause):
    count_clauses = _get_tree_listing_count_clause()

    # 'MAX(checkouts.id) as id' is necessary in this case because
    # if we just added the id in the query it would alter the GROUP BY clause,
    # potentially causing the tree listing page show the same tree multiple times
    main_query = f"""
            {with_clause}
            SELECT
                MAX(checkouts.id) AS checkout_id,
                checkouts.tree_name,
                checkouts.git_repository_branch,
                checkouts.git_repository_url,
                checkouts.git_commit_hash,
                checkouts.origin_builds_finish_time,
                checkouts.origin_tests_finish_time,
                CASE
                    WHEN COUNT(DISTINCT checkouts.git_commit_tags) > 0 THEN COALESCE(
                        ARRAY_AGG(DISTINCT checkouts.git_commit_tags) FILTER (
                            WHERE
                                checkouts.git_commit_tags IS NOT NULL
                                AND checkouts.git_commit_tags::TEXT <> '{"{}"}'
                        ),
                        ARRAY[]::TEXT[]
                    )
                    ELSE ARRAY[]::TEXT[]
                END AS git_commit_tags,
                MAX(checkouts.git_commit_name) AS git_commit_name,
                MAX(checkouts.start_time) AS start_time,
                {count_clauses}
                checkouts.origin
            FROM
                checkouts
                LEFT JOIN builds ON builds.checkout_id = checkouts.id
                LEFT JOIN tests ON tests.build_id = builds.id
                {join_clause}
            {where_clause}
            GROUP BY
                checkouts.git_commit_hash,
                checkouts.git_repository_branch,
                checkouts.git_repository_url,
                checkouts.tree_name,
                checkouts.origin_builds_finish_time,
                checkouts.origin_tests_finish_time,
                checkouts.origin
            ORDER BY
                checkouts.git_commit_hash
            """
    return main_query


def get_tree_listing_data(origin: str, interval_in_days: int) -> Optional[list[dict]]:
    params = {
        "origin_param": origin,
        "interval_param": interval_in_days,
    }

    # TODO: reuse the FIRST_TREE_CHECKOUT query
    with_clause = """
            WITH
                ORDERED_CHECKOUTS_BY_TREE AS (
                    SELECT
                        GIT_REPOSITORY_BRANCH,
                        GIT_REPOSITORY_URL,
                        GIT_COMMIT_HASH,
                        ROW_NUMBER() OVER (
                            PARTITION BY
                                GIT_REPOSITORY_BRANCH,
                                GIT_REPOSITORY_URL
                            ORDER BY
                                START_TIME DESC
                        ) AS TIME_ORDER
                    FROM
                        CHECKOUTS
                    WHERE
                        ORIGIN = %(origin_param)s
                        AND START_TIME >= NOW() - INTERVAL '%(interval_param)s days'
                ),
                FIRST_TREE_CHECKOUT AS (
                    SELECT
                        GIT_REPOSITORY_BRANCH,
                        GIT_REPOSITORY_URL,
                        GIT_COMMIT_HASH
                    FROM
                        ORDERED_CHECKOUTS_BY_TREE
                    WHERE
                        TIME_ORDER = 1
                )
    """

    # The JOIN FTC with IS NOT DISTINCT FROM is necessary because the fields can be NULL,
    # in which case a simple `WHERE (git_branch, git_url, git_hash) IN FTC` wouldn't work
    # since the NULL comparison would return UNKNOWN
    join_clause = """
                JOIN FIRST_TREE_CHECKOUT FTC ON (
                    checkouts.git_repository_branch IS NOT DISTINCT FROM FTC.GIT_REPOSITORY_BRANCH
                    AND checkouts.git_repository_url IS NOT DISTINCT FROM FTC.GIT_REPOSITORY_URL
                    AND checkouts.git_commit_hash = FTC.GIT_COMMIT_HASH
                )
    """

    where_clause = """
            WHERE
                checkouts.origin = %(origin_param)s
    """

    query = get_tree_listing_query(
        with_clause=with_clause,
        join_clause=join_clause,
        where_clause=where_clause,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return dict_fetchall(cursor=cursor)
    except ProgrammingError as e:
        if is_valid_does_not_exist_exception(e):
            set_schema_version()
            log_message(
                f"Tree Listing Status -- Schema version updated to {DEFAULT_SCHEMA_VERSION}"
            )
            return get_tree_listing_data(
                origin=origin,
                interval_in_days=interval_in_days,
            )
        else:
            raise


# TODO: rename and reuse this query
# It is being used virtually as "latest checkout from trees"
def get_tree_listing_fast(
    *, origin: Optional[str] = None, interval: dict
) -> list[Checkouts]:
    interval_timestamp = get_query_time_interval(**interval).timestamp()
    params = {"interval": interval_timestamp}

    if origin:
        origin_clause = "origin = %(origin)s AND"
        params["origin"] = origin
    else:
        origin_clause = ""

    checkouts = Checkouts.objects.raw(
        f"""
        WITH ordered_checkouts AS (
            SELECT
                id,
                tree_name,
                origin,
                git_repository_branch,
                git_repository_url,
                git_commit_hash,
                git_commit_name,
                git_commit_tags,
                patchset_hash,
                start_time,
                origin_builds_finish_time,
                origin_tests_finish_time,
                ROW_NUMBER() OVER (
                    PARTITION BY
                        git_repository_branch,
                        git_repository_url,
                        origin
                    ORDER BY start_time DESC
                ) AS time_order
            FROM
                checkouts
            WHERE
                {origin_clause}
                start_time >= TO_TIMESTAMP(%(interval)s)
        )
        SELECT
            *
        FROM
            ordered_checkouts
        WHERE
            time_order = 1
        ORDER BY
            tree_name ASC;
        """,
        params,
    )

    return list(checkouts)


def get_tree_listing_data_by_checkout_id(*, checkout_ids: list[str]):
    count_clauses = _get_tree_listing_count_clause()

    # TODO: check if those conditions of case, coalesce and group by are necessary
    query = f"""
            SELECT
                MAX(checkouts.id) AS id,
                checkouts.tree_name,
                checkouts.git_repository_branch,
                checkouts.git_repository_url,
                checkouts.git_commit_hash,
                checkouts.origin_builds_finish_time,
                checkouts.origin_tests_finish_time,
                CASE
                    WHEN COUNT(DISTINCT checkouts.git_commit_tags) > 0 THEN
                    COALESCE(
                        ARRAY_AGG(DISTINCT checkouts.git_commit_tags) FILTER (
                            WHERE checkouts.git_commit_tags IS NOT NULL
                            AND checkouts.git_commit_tags::TEXT <> '{"{}"}'
                        ),
                        ARRAY[]::TEXT[]
                    )
                    ELSE ARRAY[]::TEXT[]
                END AS git_commit_tags,
                MAX(checkouts.git_commit_name) AS git_commit_name,
                MAX(checkouts.start_time) AS start_time,
                {count_clauses}
                checkouts.origin
            FROM
                checkouts
            LEFT JOIN
                builds ON builds.checkout_id = checkouts.id
            LEFT JOIN
                tests ON tests.build_id = builds.id
            WHERE
                checkouts.id IN ({", ".join(["%s"] * len(checkout_ids))})
            GROUP BY
                checkouts.origin,
                checkouts.git_commit_hash,
                checkouts.git_repository_branch,
                checkouts.git_repository_url,
                checkouts.tree_name,
                checkouts.origin_builds_finish_time,
                checkouts.origin_tests_finish_time
            """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, checkout_ids)
            return dict_fetchall(cursor=cursor)
    except ProgrammingError as e:
        if is_valid_does_not_exist_exception(e):
            set_schema_version()
            log_message(
                f"Tree Listing By Checkout Id -- Schema version updated to {DEFAULT_SCHEMA_VERSION}"
            )
            return get_tree_listing_data_by_checkout_id(checkout_ids=checkout_ids)
        else:
            raise


def get_tree_details_data(
    origin_param: str, git_url_param: str, git_branch_param: str, commit_hash: str
) -> Optional[list[tuple]]:
    cache_key = "treeDetails"

    params = {
        "commit_hash": commit_hash,
        "origin_param": origin_param,
        "git_url_param": git_url_param,
        "git_branch_param": git_branch_param,
    }

    rows = get_query_cache(cache_key, params)
    if rows is None:
        checkout_clauses = create_checkouts_where_clauses(
            git_url=git_url_param, git_branch=git_branch_param
        )

        git_url_clause = checkout_clauses.get("git_url_clause")
        git_branch_clause = checkout_clauses.get("git_branch_clause")

        query = f"""
        SELECT
                tests.id AS tests_id,
                tests.origin,
                tests.environment_comment AS tests_environment_comment,
                tests.environment_misc AS tests_environment_misc,
                tests.path AS tests_path,
                tests.comment AS tests_comment,
                tests.log_url AS tests_log_url,
                tests.status AS tests_status,
                tests.start_time AS tests_start_time,
                tests.duration AS tests_duration,
                tests.number_value AS tests_number_value,
                tests.misc AS tests_misc,
                tests.environment_compatible AS tests_environment_compatible,
                builds_filter.*,
                incidents.id AS incidents_id,
                incidents.test_id AS incidents_test_id,
                incidents.present AS incidents_present,
                issues.id AS issues_id,
                issues.version AS issues_version,
                issues.comment AS issues_comment,
                issues.report_url AS issues_report_url
        FROM
            (
                SELECT
                    builds.id AS builds_id,
                    builds.origin,
                    builds.comment AS builds_comment,
                    builds.start_time AS builds_start_time,
                    builds.duration AS builds_duration,
                    builds.architecture AS builds_architecture,
                    builds.command AS builds_command,
                    builds.compiler AS builds_compiler,
                    builds.config_name AS builds_config_name,
                    builds.config_url AS builds_config_url,
                    builds.log_url AS builds_log_url,
                    builds.{valid_status_field()} AS builds_valid,
                    builds.misc AS builds_misc,
                    tree_head.*
                FROM
                    (
                        SELECT
                            checkouts.id AS checkout_id,
                            checkouts.git_repository_url AS checkouts_git_repository_url,
                            checkouts.git_repository_branch AS checkouts_git_repository_branch,
                            checkouts.git_commit_tags,
                            checkouts.origin as checkouts_origin
                        FROM
                            checkouts
                        WHERE
                            checkouts.git_commit_hash = %(commit_hash)s AND
                            {git_url_clause} AND
                            {git_branch_clause} AND
                            checkouts.origin = %(origin_param)s
                    ) AS tree_head
                LEFT JOIN builds
                    ON tree_head.checkout_id = builds.checkout_id
            ) AS builds_filter
        LEFT JOIN tests
            ON builds_filter.builds_id = tests.build_id
        LEFT JOIN incidents
            ON tests.id = incidents.test_id OR
               builds_filter.builds_id = incidents.build_id
        LEFT JOIN issues
            ON incidents.issue_id = issues.id
            AND incidents.issue_version = issues.version
        ORDER BY
            issues."_timestamp" DESC
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                set_query_cache(key=cache_key, params=params, rows=rows)
        except ProgrammingError as e:
            if is_valid_does_not_exist_exception(e):
                set_schema_version()
                log_message(
                    f"Tree Details -- Schema version updated to {DEFAULT_SCHEMA_VERSION}"
                )
                return get_tree_details_data(
                    origin_param=origin_param,
                    git_url_param=git_url_param,
                    commit_hash=commit_hash,
                    git_branch_param=git_branch_param,
                )
            else:
                raise

    return rows


GIT_BRANCH_FIELD = "git_repository_branch"
GIT_URL_FIELD = "git_repository_url"


def _create_selected_checkouts_clause(*, git_url: str, git_branch: str) -> str:
    tuple_fields = ["origin", "git_commit_hash"]
    none_fields = []

    if not git_branch:
        none_fields.append(GIT_BRANCH_FIELD)
    else:
        tuple_fields.append(GIT_BRANCH_FIELD)

    if not git_url:
        none_fields.append(GIT_URL_FIELD)
    else:
        tuple_fields.append(GIT_URL_FIELD)

    none_clauses = ""
    for field in none_fields:
        none_clauses += "C." + field + " IS NULL AND "

    selected_checkouts_clause = f"""
                        {none_clauses}
                        (
                            {", ".join(["C." + field for field in tuple_fields])}
                        ) IN (
                            SELECT
                                {", ".join(["EC." + field for field in tuple_fields])}
                            FROM
                                EARLIEST_COMMITS EC
                        )"""
    return selected_checkouts_clause


def get_tree_commit_history(
    commit_hash: str, origin: str, git_url: str, git_branch: str
) -> Optional[list[tuple]]:
    field_values = {
        "commit_hash": commit_hash,
        "origin_param": origin,
        "git_url_param": git_url,
        "git_branch_param": git_branch,
    }

    checkout_clauses = create_checkouts_where_clauses(
        git_url=git_url, git_branch=git_branch
    )

    git_url_clause = checkout_clauses.get("git_url_clause")
    git_branch_clause = checkout_clauses.get("git_branch_clause")

    selected_checkouts_clause = _create_selected_checkouts_clause(
        git_url=git_url, git_branch=git_branch
    )

    query = f"""
    WITH HEAD_START_TIME AS (
        SELECT
            MAX(start_time) AS HEAD_START_TIME
        FROM
            checkouts
        WHERE
            git_commit_hash = %(commit_hash)s
            AND origin = %(origin_param)s
            AND {git_url_clause}
    ),
    EARLIEST_COMMITS AS (
        SELECT
            id,
            git_commit_hash,
            git_commit_name,
            git_repository_branch,
            git_repository_url,
            git_commit_tags,
            origin,
            start_time,
            time_order
        FROM (
            SELECT
                id,
                git_commit_hash,
                git_commit_name,
                git_repository_branch,
                git_repository_url,
                git_commit_tags,
                origin,
                start_time,
                ROW_NUMBER() OVER (
                    PARTITION BY
                        git_repository_url,
                        git_repository_branch,
                        origin,
                        git_commit_hash
                    ORDER BY
                        start_time DESC
                ) AS time_order
            FROM
                checkouts
            WHERE
                {git_branch_clause}
                AND {git_url_clause}
                AND origin = %(origin_param)s
                AND git_commit_hash IS NOT NULL
                AND start_time <= (
                    SELECT
                        *
                    FROM
                        HEAD_START_TIME
                )
            ORDER BY
                start_time DESC
        ) AS CHECKOUTS_TIME_ORDER
    WHERE
        TIME_ORDER = 1
    LIMIT
        6
    ),
    SELECTED_CHECKOUTS AS (
        SELECT
            c.id,
            c.git_commit_hash,
            c.git_commit_name,
            c.git_commit_tags,
            c.start_time
        FROM
            checkouts c
        WHERE
            {selected_checkouts_clause}
            AND c.start_time <= (
                SELECT
                    *
                FROM
                    HEAD_START_TIME
            )
        ORDER BY
            c.start_time DESC
    )
    SELECT
        c.git_commit_hash,
        c.git_commit_name,
        c.git_commit_tags,
        c.start_time,
        b.duration,
        b.architecture,
        b.compiler,
        b.config_name,
        b.{valid_status_field()},
        t.path,
        t.status,
        t.duration,
        t.environment_compatible,
        t.environment_misc,
        b.id AS build_id,
        b.misc AS build_misc,
        t.id AS test_id,
        ic.id AS incidents_id,
        ic.test_id AS incidents_test_id,
        i.id AS issues_id,
        i.version AS issues_version
    FROM
        SELECTED_CHECKOUTS AS c
        LEFT JOIN builds AS b ON c.id = b.checkout_id
        LEFT JOIN tests AS t ON t.build_id = b.id
        LEFT JOIN incidents AS ic ON t.id = ic.test_id
        OR b.id = ic.build_id
        LEFT JOIN issues AS i ON ic.issue_id = i.id
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                field_values,
            )
            return cursor.fetchall()
    except ProgrammingError as e:
        if is_valid_does_not_exist_exception(e):
            set_schema_version()
            log_message(
                f"Tree Commit History -- Schema version updated to {DEFAULT_SCHEMA_VERSION}"
            )
            return get_tree_commit_history(
                commit_hash=commit_hash,
                origin=origin,
                git_url=git_url,
                git_branch=git_branch,
            )
        else:
            raise


def get_latest_tree(
    *,
    tree_name: str,
    branch: str,
    origin: str,
    git_commit_hash: Optional[str] = None,
) -> Optional[dict]:
    """Retrieves the most recent occurrence of the checkout of a tree with the given params."""

    tree_fields = [
        "git_commit_hash",
        "git_commit_name",
        "git_repository_url",
        "tree_name",
        "origin",
    ]

    query = Checkouts.objects.values(*tree_fields).filter(
        origin=origin,
        git_repository_branch=branch,
        tree_name=tree_name,
    )

    if git_commit_hash is not None:
        query = query.filter(git_commit_hash=git_commit_hash)
    else:
        query = query.filter(git_commit_hash__isnull=False)

    query = query.order_by("-start_time").first()

    return query
