from typing import TypedDict, Optional
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


class IntervalInDays(TypedDict):
    days: int


def get_tree_listing_data(
    origin: str, interval_in_days: IntervalInDays
) -> Optional[list[tuple]]:
    count_clauses = _get_tree_listing_count_clause()

    params = {
        "origin_param": origin,
        "interval_param": get_query_time_interval(**interval_in_days).timestamp(),
    }

    # '1 as id' is necessary in this case because django raw queries must include the primary key.
    # In this case we don't need the primary key and adding it would alter the GROUP BY clause,
    # potentially causing the tree listing page show the same tree multiple times
    query = f"""
            SELECT
                MAX(checkouts.id) as id,
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
                COALESCE(
                    ARRAY_AGG(DISTINCT tree_name) FILTER (
                        WHERE tree_name IS NOT NULL
                    ),
                    ARRAY[]::TEXT[]
                ) AS tree_names,
                checkouts.origin
            FROM
                checkouts
            LEFT JOIN
                builds ON builds.checkout_id = checkouts.id
            LEFT JOIN
                tests ON tests.build_id = builds.id
            WHERE
                checkouts.git_commit_hash IN (
                    SELECT
                        git_commit_hash
                    FROM
                        (
                            SELECT
                                git_repository_branch,
                                git_repository_url,
                                git_commit_hash,
                                ROW_NUMBER() OVER (
                                    PARTITION BY
                                        git_repository_url,
                                        git_repository_branch,
                                        origin
                                    ORDER BY start_time DESC
                                ) AS time_order
                            FROM
                                checkouts
                            WHERE
                                origin = %(origin_param)s
                                AND start_time >= TO_TIMESTAMP(%(interval_param)s)
                        ) AS ordered_checkouts_by_tree
                    WHERE
                        time_order = 1
                    ORDER BY
                        git_repository_branch,
                        git_repository_url,
                        time_order
                )
                AND checkouts.origin = %(origin_param)s
            GROUP BY
                checkouts.git_commit_hash,
                checkouts.git_repository_branch,
                checkouts.git_repository_url,
                checkouts.tree_name,
                checkouts.origin_builds_finish_time,
                checkouts.origin_tests_finish_time,
                checkouts.origin
            ORDER BY
                checkouts.git_commit_hash;
            ;
            """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
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
def get_tree_listing_fast(*, origin: Optional[str] = None, interval: dict):
    origin_clause = f"origin = '{origin}' AND" if origin is not None else ""
    interval_timestamp = get_query_time_interval(**interval).timestamp()

    checkouts = Checkouts.objects.raw(
        f"""
        WITH ordered_checkouts AS (
            SELECT
                id,
                tree_name,
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
                        git_repository_url,
                        git_repository_branch,
                        origin
                    ORDER BY start_time DESC
                ) AS time_order
            FROM
                checkouts
            WHERE
                {origin_clause}
                start_time >= TO_TIMESTAMP({interval_timestamp})
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
    )

    return checkouts


def get_tree_listing_data_by_checkout_id(*, checkout_ids: list[str]):
    count_clauses = _get_tree_listing_count_clause()

    # TODO: check if those conditions of case, coalesce and group by are necessary
    query = f"""
            SELECT
                MAX(checkouts.id) AS id,
                checkouts.origin,
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
                COALESCE(
                    ARRAY_AGG(DISTINCT tree_name) FILTER (
                        WHERE tree_name IS NOT NULL
                    ),
                    ARRAY[]::TEXT[]
                ) AS tree_names
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
                tests.origin AS tests_origin,
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
                WHERE
                    tree_head.checkouts_origin = %(origin_param)s
            ) AS builds_filter
        LEFT JOIN tests
            ON builds_filter.builds_id = tests.build_id
        LEFT JOIN incidents
            ON tests.id = incidents.test_id OR
               builds_filter.builds_id = incidents.build_id
        LEFT JOIN issues
            ON incidents.issue_id = issues.id
            AND incidents.issue_version = issues.version
        WHERE
            tests.origin = %(origin_param)s OR
            tests.origin IS NULL
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

    query = f"""
    WITH earliest_commits AS (
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
                    PARTITION BY git_repository_url, git_repository_branch, origin, git_commit_hash
                    ORDER BY start_time DESC
                ) AS time_order
            FROM   checkouts
            WHERE  {git_branch_clause}
                AND {git_url_clause}
                AND origin = %(origin_param)s
                AND git_commit_hash IS NOT NULL
                AND start_time <= (SELECT Max(start_time) AS head_start_time
                                    FROM   checkouts
                                    WHERE  git_commit_hash = %(commit_hash)s
                                            AND origin = %(origin_param)s
                                            AND {git_url_clause})
            ORDER  BY start_time DESC) AS checkouts_time_order
        WHERE
            time_order = 1
        LIMIT 6
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
    FROM earliest_commits AS c
    LEFT JOIN builds AS b
    ON
        c.id = b.checkout_id
    LEFT JOIN tests AS t
    ON
        t.build_id = b.id
    LEFT JOIN incidents AS ic
        ON t.id = ic.test_id OR
            b.id = ic.build_id
    LEFT JOIN issues AS i
        ON ic.issue_id = i.id
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
