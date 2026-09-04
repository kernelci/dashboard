from typing import TYPE_CHECKING, Literal, Optional

from django.db import connection
from django.db.models import Q

from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.helpers.treeCompare import (
    build_boot_test_compare_filter_clauses,
    build_build_compare_filter_clauses,
)
from kernelCI_app.helpers.treeDetails import create_checkouts_where_clauses
from kernelCI_app.models import Checkouts
from kernelCI_app.queries.duration import (
    get_boot_test_duration_clause,
    get_build_duration_clause,
)

if TYPE_CHECKING:
    from kernelCI_app.helpers.filters import FilterParams


def _get_tree_listing_count_clause() -> str:
    build_count_clause = """
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


def get_tree_listing_data_denormalized(
    *, origin: str, interval_in_days: int
) -> Optional[list[tuple]]:
    interval_param = f"{interval_in_days} days"
    params = {
        "origin_param": origin,
        "interval_param": interval_param,
    }

    with connection.cursor() as cursor:
        cursor.execute(
            """
            WITH latest AS (
                SELECT
                    checkout_id
                FROM
                    latest_checkout
                WHERE
                    start_time >= NOW() - INTERVAL %(interval_param)s
                    AND origin = %(origin_param)s
            )
            SELECT
                tl.checkout_id,
                tl.origin,
                tl.tree_name,
                tl.git_repository_url,
                tl.git_repository_branch,
                tl.git_commit_hash,
                tl.git_commit_name,
                tl.git_commit_tags,
                tl.start_time,
                tl.build_pass,
                tl.build_failed,
                tl.build_inc,
                tl.boot_pass,
                tl.boot_failed,
                tl.boot_inc,
                tl.test_pass,
                tl.test_failed,
                tl.test_inc
            FROM
                tree_listing tl
                JOIN latest l ON tl.checkout_id = l.checkout_id
            """,
            params,
        )
        return cursor.fetchall()


def get_tree_details_data(
    *,
    origin_param: str,
    git_url_param: Optional[str],
    git_branch_param: Optional[str],
    commit_hash: Optional[str],
    tree_name: Optional[str] = None,
) -> Optional[list[tuple]]:
    cache_key = "treeDetails"

    params = {
        "commit_hash": commit_hash,
        "tree_name": tree_name,
        "origin_param": origin_param,
        "git_url_param": git_url_param,
        "git_branch_param": git_branch_param,
    }

    rows = get_query_cache(cache_key, params)
    if rows is None:
        checkout_clauses = create_checkouts_where_clauses(
            git_url=git_url_param,
            git_branch=git_branch_param,
            tree_name=tree_name,
        )

        git_branch_clause = checkout_clauses.get("git_branch_clause")
        tree_name_clause = checkout_clauses.get("tree_name_clause")
        git_url_clause = checkout_clauses.get("git_url_clause")
        tree_name_full_clause = "AND " + tree_name_clause if tree_name_clause else ""
        git_url_full_clause = "AND " + git_url_clause if git_url_clause else ""

        query = f"""
        WITH RELEVANT_HASH AS (
            SELECT
                c.git_commit_hash
            FROM
                checkouts c
            WHERE
                c.git_commit_hash = %(commit_hash)s
                OR %(commit_hash)s = ANY (c.git_commit_tags)
            ORDER BY
                c._timestamp DESC
            LIMIT 1
        )
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
                -- TODO remove misc->>'runtime' fallback after lab backfill
                COALESCE(test_labs.name, tests.misc ->> 'runtime') AS tests_lab,
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
                    builds.status AS builds_valid,
                    builds.misc AS builds_misc,
                    COALESCE(build_labs.name, builds.misc ->> 'lab') AS builds_lab,
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
                            checkouts.git_commit_hash = (
                                SELECT git_commit_hash FROM RELEVANT_HASH
                            )
                            {git_url_full_clause}
                            {tree_name_full_clause}
                            AND {git_branch_clause}
                            AND checkouts.origin = %(origin_param)s
                    ) AS tree_head
                LEFT JOIN builds
                    ON tree_head.checkout_id = builds.checkout_id
                LEFT JOIN labs AS build_labs
                    ON builds.lab_id = build_labs.id
            ) AS builds_filter
        LEFT JOIN tests
            ON builds_filter.builds_id = tests.build_id
        LEFT JOIN labs AS test_labs
            ON tests.lab_id = test_labs.id
        LEFT JOIN incidents
            ON tests.id = incidents.test_id OR
               builds_filter.builds_id = incidents.build_id
        LEFT JOIN issues
            ON incidents.issue_id = issues.id
            AND incidents.issue_version = issues.version
        ORDER BY
            issues."_timestamp" DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            set_query_cache(key=cache_key, params=params, rows=rows)

    return rows


def get_tree_details_rollup(
    *,
    origin_param: str,
    git_url_param: Optional[str],
    git_branch_param: Optional[str],
    commit_hash: Optional[str],
    tree_name: Optional[str] = None,
) -> Optional[list[dict]]:
    """
    Fetch denormalized test/boot rollup data for a given tree commit.

    Returns aggregated data from tree_tests_rollup table which pre-aggregates
    test results by various dimensions (path_group, config, arch, compiler,
    hardware, platform, lab, origin, and issue).
    """
    cache_key = "treeDetailsRollup"

    params = {
        "commit_hash": commit_hash,
        "tree_name": tree_name,
        "origin_param": origin_param,
        "git_url_param": git_url_param,
        "git_branch_param": git_branch_param,
    }

    rows = get_query_cache(cache_key, params)
    if rows is None:
        checkout_clauses = create_checkouts_where_clauses(
            git_url=git_url_param,
            git_branch=git_branch_param,
            tree_name=tree_name,
        )

        git_branch_clause = checkout_clauses.get("git_branch_clause")
        tree_name_clause = checkout_clauses.get("tree_name_clause")
        git_url_clause = checkout_clauses.get("git_url_clause")
        tree_name_full_clause = "AND " + tree_name_clause if tree_name_clause else ""
        git_url_full_clause = "AND " + git_url_clause if git_url_clause else ""

        query = f"""
        WITH RELEVANT_CHECKOUTS AS (
            SELECT
                c.git_commit_hash,
                c.tree_name,
                c.git_repository_branch,
                c.git_repository_url,
                c.origin
            FROM
                checkouts c
            WHERE
                (c.git_commit_hash = %(commit_hash)s
                OR %(commit_hash)s = ANY (c.git_commit_tags))
                {git_url_full_clause}
                {tree_name_full_clause}
                AND {git_branch_clause}
                AND c.origin = %(origin_param)s
            ORDER BY
                c._timestamp DESC
            LIMIT 1
        )
        SELECT
            tr.origin,
            tr.tree_name,
            tr.git_repository_branch,
            tr.git_repository_url,
            tr.git_commit_hash,
            tr.path_group,
            tr.build_config_name,
            tr.build_architecture,
            tr.build_compiler,
            tr.hardware_key,
            tr.test_platform,
            tr.test_lab,
            tr.test_origin,
            tr.issue_id,
            tr.issue_version,
            tr.issue_uncategorized,
            tr.is_boot,
            tr.pass_tests,
            tr.fail_tests,
            tr.skip_tests,
            tr.error_tests,
            tr.miss_tests,
            tr.done_tests,
            tr.null_tests,
            tr.total_tests,
            i.comment AS issue_comment,
            i.report_url AS issue_report_url
        FROM
            tree_tests_rollup tr
        INNER JOIN RELEVANT_CHECKOUTS rc ON (
            tr.git_commit_hash = rc.git_commit_hash
            AND tr.origin = rc.origin
            AND tr.tree_name IS NOT DISTINCT FROM rc.tree_name
            AND tr.git_repository_branch IS NOT DISTINCT FROM rc.git_repository_branch
            AND tr.git_repository_url IS NOT DISTINCT FROM rc.git_repository_url
        )
        LEFT JOIN issues i
            ON tr.issue_id = i.id AND tr.issue_version = i.version
        ORDER BY
            tr.total_tests DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = dict_fetchall(cursor=cursor)
            set_query_cache(key=cache_key, params=params, rows=rows)

    return rows


def get_tree_data(
    *,
    data_type: Literal["builds", "boots", "tests"],
    origin_param: str,
    git_url_param: Optional[str],
    git_branch_param: Optional[str],
    commit_hash: Optional[str],
    tree_name: Optional[str] = None,
) -> Optional[list[tuple]]:
    """Fetch build, boot, or test rows for a given tree commit."""
    cache_key = f"treeDetails{data_type.capitalize()}"

    params = {
        "commit_hash": commit_hash,
        "tree_name": tree_name,
        "origin_param": origin_param,
        "git_url_param": git_url_param,
        "git_branch_param": git_branch_param,
    }

    rows = get_query_cache(cache_key, params)
    if rows is None:
        checkout_clauses = create_checkouts_where_clauses(
            git_url=git_url_param,
            git_branch=git_branch_param,
            tree_name=tree_name,
        )

        git_branch_clause = checkout_clauses.get("git_branch_clause")
        tree_name_clause = checkout_clauses.get("tree_name_clause")
        git_url_clause = checkout_clauses.get("git_url_clause")
        tree_name_full_clause = "AND " + tree_name_clause if tree_name_clause else ""
        git_url_full_clause = "AND " + git_url_clause if git_url_clause else ""

        is_boots = data_type == "boots"
        is_tests = data_type == "tests"
        include_test_cols = is_boots or is_tests

        tests_select = (
            """
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
                tests.environment_compatible AS tests_environment_compatible,"""
            if include_test_cols
            else """
                NULL AS tests_id,
                NULL AS tests_origin,
                NULL AS tests_environment_comment,
                NULL AS tests_environment_misc,
                NULL AS tests_path,
                NULL AS tests_comment,
                NULL AS tests_log_url,
                NULL AS tests_status,
                NULL AS tests_start_time,
                NULL AS tests_duration,
                NULL AS tests_number_value,
                NULL AS tests_misc,
                NULL AS tests_environment_compatible,"""
        )

        # TODO remove misc->>'runtime' fallback after lab backfill
        test_lab_select = (
            "COALESCE(test_labs.name, tests.misc->>'runtime') AS test_lab,"
            if include_test_cols
            else "NULL AS test_lab,"
        )

        tests_join = ""
        if is_boots:
            tests_join = (
                "LEFT JOIN tests ON builds_filter.builds_id = tests.build_id"
                " AND (tests.path = 'boot' OR tests.path LIKE 'boot.%%')"
                " LEFT JOIN labs AS test_labs ON tests.lab_id = test_labs.id"
            )
        elif is_tests:
            tests_join = (
                "LEFT JOIN tests ON builds_filter.builds_id = tests.build_id"
                " AND tests.path <> 'boot' AND tests.path NOT LIKE 'boot.%%'"
                " LEFT JOIN labs AS test_labs ON tests.lab_id = test_labs.id"
            )

        incidents_on = (
            "tests.id = incidents.test_id"
            if include_test_cols
            else "builds_filter.builds_id = incidents.build_id"
        )

        query = f"""
        WITH RELEVANT_HASH AS (
            SELECT
                c.git_commit_hash
            FROM
                checkouts c
            WHERE
                c.git_commit_hash = %(commit_hash)s
                OR %(commit_hash)s = ANY (c.git_commit_tags)
            ORDER BY
                c._timestamp DESC
            LIMIT 1
        )
        SELECT
            {tests_select}
                {test_lab_select}
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
                    builds.status AS builds_valid,
                    builds.misc AS builds_misc,
                    -- TODO remove misc->>'lab' fallback after lab backfill
                    COALESCE(build_labs.name, builds.misc->>'lab') AS build_lab,
                    tree_head.*
                FROM
                    (
                        SELECT
                            checkouts.id AS checkout_id,
                            checkouts.git_repository_url AS checkouts_git_repository_url,
                            checkouts.git_repository_branch AS checkouts_git_repository_branch,
                            checkouts.git_commit_tags AS checkout_git_commit_tags,
                            checkouts.origin AS checkouts_origin
                        FROM
                            checkouts
                        WHERE
                            checkouts.git_commit_hash = (
                                SELECT git_commit_hash FROM RELEVANT_HASH
                            )
                            {git_url_full_clause}
                            {tree_name_full_clause}
                            AND {git_branch_clause}
                            AND checkouts.origin = %(origin_param)s
                    ) AS tree_head
                LEFT JOIN builds
                    ON tree_head.checkout_id = builds.checkout_id
                LEFT JOIN labs AS build_labs
                    ON builds.lab_id = build_labs.id
            ) AS builds_filter
        {tests_join}
        LEFT JOIN incidents
            ON {incidents_on}
        LEFT JOIN issues
            ON incidents.issue_id = issues.id
            AND incidents.issue_version = issues.version
        ORDER BY
            issues."_timestamp" DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            set_query_cache(key=cache_key, params=params, rows=rows)

    return rows


def get_tree_details_builds(
    *,
    origin_param: str,
    git_url_param: Optional[str],
    git_branch_param: Optional[str],
    commit_hash: Optional[str],
    tree_name: Optional[str] = None,
) -> Optional[list[dict]]:
    """
    Fetch builds for a given tree commit.
    """
    cache_key = "treeDetailsBuildsData"

    params = {
        "commit_hash": commit_hash,
        "tree_name": tree_name,
        "origin_param": origin_param,
        "git_url_param": git_url_param,
        "git_branch_param": git_branch_param,
    }

    rows = get_query_cache(cache_key, params)
    if rows is None:
        checkout_clauses = create_checkouts_where_clauses(
            git_url=git_url_param,
            git_branch=git_branch_param,
            tree_name=tree_name,
        )

        git_branch_clause = checkout_clauses.get("git_branch_clause")
        tree_name_clause = checkout_clauses.get("tree_name_clause")
        git_url_clause = checkout_clauses.get("git_url_clause")
        tree_name_full_clause = "AND " + tree_name_clause if tree_name_clause else ""
        git_url_full_clause = "AND " + git_url_clause if git_url_clause else ""

        query = f"""
        WITH RELEVANT_CHECKOUTS AS (
            SELECT
                c.id AS checkout_id,
                c.git_repository_url,
                c.git_repository_branch,
                c.git_commit_tags,
                c.origin
            FROM
                checkouts c
            WHERE
                (c.git_commit_hash = %(commit_hash)s
                OR %(commit_hash)s = ANY (c.git_commit_tags))
                {git_url_full_clause}
                {tree_name_full_clause}
                AND {git_branch_clause}
                AND c.origin = %(origin_param)s
            ORDER BY
                c._timestamp DESC
        )
        SELECT
            b.id AS build_id,
            b.origin AS build_origin,
            b.comment AS build_comment,
            b.start_time AS build_start_time,
            b.duration AS build_duration,
            b.architecture AS build_architecture,
            b.command AS build_command,
            b.compiler AS build_compiler,
            b.config_name AS build_config_name,
            b.config_url AS build_config_url,
            b.log_url AS build_log_url,
            b.status AS build_status,
            b.misc AS build_misc,
            -- TODO remove misc->>'lab' fallback after lab backfill
            COALESCE(bl.name, b.misc->>'lab') AS build_lab,
            rc.checkout_id,
            rc.git_repository_url AS checkout_git_repository_url,
            rc.git_repository_branch AS checkout_git_repository_branch,
            rc.git_commit_tags AS checkout_git_commit_tags,
            rc.origin AS checkout_origin,
            inc.id AS incident_id,
            inc.test_id AS incident_test_id,
            inc.present AS incident_present,
            iss.id AS issue_id,
            iss.version AS issue_version,
            iss.comment AS issue_comment,
            iss.report_url AS issue_report_url
        FROM
            builds b
        INNER JOIN RELEVANT_CHECKOUTS rc ON b.checkout_id IN (SELECT checkout_id FROM RELEVANT_CHECKOUTS)
        LEFT JOIN labs bl
            ON b.lab_id = bl.id
        LEFT JOIN incidents inc
            ON inc.build_id = b.id AND inc.test_id IS NULL
        LEFT JOIN issues iss
            ON inc.issue_id = iss.id AND inc.issue_version = iss.version
        ORDER BY
            iss."_timestamp" DESC NULLS LAST,
            b.start_time DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = dict_fetchall(cursor=cursor)
            set_query_cache(key=cache_key, params=params, rows=rows)

    return rows


GIT_BRANCH_FIELD = "git_repository_branch"
GIT_URL_FIELD = "git_repository_url"


def _create_selected_checkouts_clause(
    *,
    git_url: str,
    git_branch: str,
    tree_name: Optional[str],
) -> str:
    tuple_fields = ["origin", "git_commit_hash"]
    none_fields = []

    if not git_branch:
        none_fields.append(GIT_BRANCH_FIELD)
    else:
        tuple_fields.append(GIT_BRANCH_FIELD)

    if tree_name:
        tuple_fields.append("tree_name")

    if not git_url:
        if not tree_name:
            # Only query for git_url NULL if we know that its value is NULL, not just if it wasn't passed
            # This means to only query if I know it didn't come from treeDetailsDirect
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


def get_tree_commits(
    *,
    origin: Optional[str],
    git_url: Optional[str],
    git_branch: Optional[str],
    tree_name: Optional[str],
):
    cache_key = "treeCommits"

    params = {
        "git_repository_url": git_url,
        "git_branch": git_branch,
        "tree_name": tree_name,
        "origin": origin,
    }

    rows = get_query_cache(cache_key, params)
    if rows is not None:
        return rows

    if origin:
        origin_clause = "\nAND origin = %(origin)s"
    else:
        origin_clause = "\nAND origin IS NULL"

    url_clause = ""
    if git_url:
        url_clause = "\nAND git_repository_url = %(git_repository_url)s"

    query = f"""
        SELECT
            git_commit_hash,
            MAX(start_time) AS start_time_end,
            MAX(git_commit_name) AS git_commit_name,
            COALESCE(
                ARRAY_AGG(DISTINCT tag) FILTER (WHERE tag IS NOT NULL),
                ARRAY[]::text[]
            ) AS git_commit_tags
        FROM
            checkouts
            LEFT JOIN LATERAL unnest(git_commit_tags) AS tag ON true
        WHERE
            tree_name = %(tree_name)s
            AND git_repository_branch = %(git_branch)s
            {url_clause}
            {origin_clause}
        GROUP BY
            git_commit_hash
        ORDER BY
            start_time_end DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = dict_fetchall(cursor)
        set_query_cache(key=cache_key, params=params, rows=rows)
        return rows


def union_all(queries: list[str]) -> str:
    return " UNION ALL ".join(f"({query})" for query in queries)


def _get_platform_filter_clause(platform_filter: Optional[list[str]]) -> str:
    if platform_filter:
        return """
        AND (tests.environment_compatible && %(platform)s::text[]
            OR tests.environment_misc->>'platform' = ANY(%(platform)s::text[]))
        """
    return ""


def _get_builds_platform_filter_clause(platform_filter: Optional[list[str]]) -> str:
    if platform_filter:
        return """
        AND EXISTS (
            SELECT 1 FROM tests
            WHERE tests.build_id = builds.id
              AND (tests.environment_compatible && %(platform)s::text[]
                   OR tests.environment_misc->>'platform' = ANY(%(platform)s::text[]))
        )
        """
    return ""


def get_tree_commit_history_hashes_aggregated(
    *,
    commit_hashes: list[str],
    origin: str,
    git_url: Optional[str],
    git_branch: Optional[str],
    tree_name: Optional[str],
    platform_filter: list[str] = None,
    include_types: Optional[list[str]] = None,
    builds_duration: tuple[Optional[int], Optional[int]] = (None, None),
    boots_duration: tuple[Optional[int], Optional[int]] = (None, None),
    tests_duration: tuple[Optional[int], Optional[int]] = (None, None),
) -> list[dict]:

    if not commit_hashes:
        return []

    if not include_types:
        include_types = ["builds", "boots", "tests"]

    include_types = [t.lower() for t in include_types]

    build_duration_min, build_duration_max = builds_duration
    boot_duration_min, boot_duration_max = boots_duration
    test_duration_min, test_duration_max = tests_duration

    build_duration_clause = get_build_duration_clause(builds_duration)
    boots_tests_duration_clause = get_boot_test_duration_clause(
        boots_duration, tests_duration
    )

    params = {
        "commit_hashes": commit_hashes,
        "origin_param": origin,
        "git_url_param": git_url,
        "git_branch_param": git_branch,
        "tree_name": tree_name,
        "platform": platform_filter,
        "build_duration_min": build_duration_min,
        "build_duration_max": build_duration_max,
        "boot_duration_min": boot_duration_min,
        "boot_duration_max": boot_duration_max,
        "test_duration_min": test_duration_min,
        "test_duration_max": test_duration_max,
    }

    cache_key = "treeCommitHistoryHashesAggregatedNoCompatibles"
    cache_params = {
        **params,
        "include_types": tuple(sorted(include_types)),
    }
    rows = get_query_cache(cache_key, cache_params)
    if rows is not None:
        return rows

    checkout_clauses = create_checkouts_where_clauses(
        git_url=git_url, git_branch=git_branch, tree_name=tree_name
    )

    git_branch_clause = checkout_clauses.get("git_branch_clause")
    tree_name_clause = checkout_clauses.get("tree_name_clause")
    git_url_clause = checkout_clauses.get("git_url_clause")
    tree_name_full_clause = "\nAND " + tree_name_clause if tree_name_clause else ""
    git_url_full_clause = "\nAND " + git_url_clause if git_url_clause else ""
    git_branch_full_clause = "\nAND " + git_branch_clause if git_branch_clause else ""

    include_builds = "builds" in include_types
    include_tests = "tests" in include_types
    include_boots = "boots" in include_types

    platform_filter_clause = _get_platform_filter_clause(platform_filter)

    builds_platform_filter_clause = _get_builds_platform_filter_clause(platform_filter)

    builds_query = f"""
        SELECT
            COUNT(DISTINCT builds.id) AS count,
            c.git_commit_hash,
            c.git_commit_name,
            c.git_commit_tags,
            c.start_time,
            c.origin,
            builds.status AS status,
            array[builds.compiler, builds.architecture] AS compiler_arch,
            builds.config_name AS config_name,
            -- TODO remove misc->>'lab' fallback after lab backfill
            COALESCE(bl.name, builds.misc->>'lab') AS lab,
            ARRAY_AGG(DISTINCT ic.issue_id || ',' || ic.issue_version::text) AS known_issues,
            true AS is_build,
            false AS is_boot,
            false AS is_test
        FROM checkouts c
        INNER JOIN builds ON c.id = builds.checkout_id
        LEFT JOIN labs bl ON builds.lab_id = bl.id
        LEFT JOIN incidents ic ON builds.id = ic.build_id
        WHERE
            c.git_commit_hash = ANY(%(commit_hashes)s)
            AND c.origin = %(origin_param)s
            AND builds.config_name IS NOT NULL
            AND builds.id NOT LIKE 'maestro:dummy_%%'
            {builds_platform_filter_clause}
            {git_branch_full_clause}
            {git_url_full_clause}
            {tree_name_full_clause}
            {build_duration_clause}
        GROUP BY
            c.id,
            builds.status,
            builds.compiler,
            builds.architecture,
            builds.config_name,
            lab
    """

    boot_filter = ""
    if include_boots and not include_tests:
        boot_filter = "\nAND (tests.path ='boot' OR tests.path LIKE 'boot.%%')"
    elif include_tests and not include_boots:
        boot_filter = "\nAND (tests.path != 'boot' AND tests.path NOT LIKE 'boot.%%')"

    tests_query = f"""
        SELECT
            COUNT(DISTINCT tests.id) AS count,
            c.git_commit_hash,
            c.git_commit_name,
            c.git_commit_tags,
            c.start_time,
            c.origin,
            tests.status AS status,
            array[builds.compiler, builds.architecture] AS compiler_arch,
            builds.config_name AS config_name,
            -- TODO remove misc->>'runtime' fallback after lab backfill
            COALESCE(tl.name, tests.misc->>'runtime') AS lab,
            ARRAY_AGG(DISTINCT ic.issue_id || ',' || ic.issue_version::text) AS known_issues,
            false AS is_build,
            true AS is_test,
            (tests.path like 'boot.%%' or tests.path = 'boot') AS is_boot
        FROM checkouts c
        INNER JOIN builds ON c.id = builds.checkout_id
        INNER JOIN tests ON tests.build_id = builds.id {boot_filter}
        LEFT JOIN labs tl ON tests.lab_id = tl.id
        LEFT JOIN incidents ic ON tests.id = ic.test_id
        LEFT JOIN issues i ON ic.issue_id = i.id
        WHERE
            c.git_commit_hash = ANY(%(commit_hashes)s)
            AND c.origin = %(origin_param)s
            {platform_filter_clause}
            {git_branch_full_clause}
            {git_url_full_clause}
            {tree_name_full_clause}
            {boots_tests_duration_clause}
        GROUP BY
            c.id,
            c.start_time,
            c.origin,
            tests.status,
            is_boot,
            builds.compiler,
            builds.architecture,
            builds.config_name,
            lab
    """

    queries = []
    if include_builds:
        queries.append(builds_query)
    if include_boots or include_tests:
        queries.append(tests_query)

    if not queries:
        set_query_cache(key=cache_key, params=cache_params, rows=[])
        return []

    query = union_all(queries)

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = dict_fetchall(cursor)
        set_query_cache(key=cache_key, params=cache_params, rows=rows)
        return rows


def get_tree_compare_boots_tests_diff(
    *,
    data_type: Literal["boots", "tests"],
    hash_a: str,
    hash_b: str,
    origin: str,
    git_branch: str,
    tree_name: str,
    filters: Optional["FilterParams"] = None,
    boots_duration: tuple[Optional[int], Optional[int]] = (None, None),
    tests_duration: tuple[Optional[int], Optional[int]] = (None, None),
) -> list[dict]:
    """Return boot/test rows whose latest grouped status differs between commits.

    Identity key: path + config_name + architecture + platform.
    Uses the latest checkout per hash and the latest test row per identity key
    (same latest-wins semantics as get_tree_compare_builds_diff).

    Duration kwargs are accepted for call-site compat but ignored: filtering by
    duration before the A/B join invents false appeared/disappeared rows.
    """
    del (
        boots_duration,
        tests_duration,
    )  # ponytail: post-join duration needs selected cols
    commit_hashes = [hash_a, hash_b]
    filter_sql = build_boot_test_compare_filter_clauses(filters, data_type)

    params = {
        "hash_a": hash_a,
        "hash_b": hash_b,
        "commit_hashes": commit_hashes,
        "origin_param": origin,
        "git_branch_param": git_branch,
        "tree_name": tree_name,
        "unknown_string": UNKNOWN_STRING,
        **filter_sql.params,
    }

    cache_key = "treeCompareBootsTestsDiff"
    cache_params = {
        **params,
        "data_type": data_type,
        "commit_hashes": tuple(sorted(commit_hashes)),
        "filter_pre_join": filter_sql.pre_join,
        "filter_post_join": filter_sql.post_join,
    }
    rows = get_query_cache(cache_key, cache_params)
    if rows is not None:
        return rows

    git_branch_clause, tree_name_full_clause = _get_compare_checkout_clauses(
        git_branch_param=git_branch,
        tree_name=tree_name,
    )

    if data_type == "boots":
        path_filter = "AND (t.path = 'boot' OR t.path LIKE 'boot.%%')"
    else:
        path_filter = "AND t.path IS DISTINCT FROM 'boot' AND t.path NOT LIKE 'boot.%%'"

    query = f"""
        WITH RELEVANT_CHECKOUTS AS (
            SELECT DISTINCT ON (c.git_commit_hash)
                c.id AS checkout_id,
                c.git_commit_hash
            FROM
                checkouts c
            WHERE
                c.git_commit_hash = ANY(%(commit_hashes)s)
                {tree_name_full_clause}
                AND {git_branch_clause}
                AND c.origin = %(origin_param)s
            ORDER BY
                c.git_commit_hash,
                c._timestamp DESC
        ),
        TEST_ROWS AS (
            SELECT DISTINCT ON (
                rc.git_commit_hash,
                COALESCE(NULLIF(t.path, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s),
                COALESCE(
                    NULLIF(t.environment_misc->>'platform', ''),
                    %(unknown_string)s
                )
            )
                rc.git_commit_hash,
                COALESCE(NULLIF(t.path, ''), %(unknown_string)s) AS path,
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s)
                    AS config_name,
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s)
                    AS architecture,
                COALESCE(
                    NULLIF(t.environment_misc->>'platform', ''),
                    %(unknown_string)s
                ) AS platform,
                CASE
                    WHEN UPPER(t.status) = 'PASS' THEN 'PASS'
                    WHEN UPPER(t.status) = 'FAIL' THEN 'FAIL'
                    ELSE 'INCONCLUSIVE'
                END AS grouped_status
            FROM
                RELEVANT_CHECKOUTS rc
            INNER JOIN builds b ON b.checkout_id = rc.checkout_id
            INNER JOIN tests t ON t.build_id = b.id
                {path_filter}
            WHERE
                b.id NOT LIKE 'maestro:dummy_%%'
                {filter_sql.pre_join}
            ORDER BY
                rc.git_commit_hash,
                COALESCE(NULLIF(t.path, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s),
                COALESCE(
                    NULLIF(t.environment_misc->>'platform', ''),
                    %(unknown_string)s
                ),
                t.start_time DESC NULLS LAST,
                t._timestamp DESC NULLS LAST
        ),
        SIDE_A AS (
            SELECT path, config_name, architecture, platform, grouped_status
            FROM TEST_ROWS
            WHERE git_commit_hash = %(hash_a)s
        ),
        SIDE_B AS (
            SELECT path, config_name, architecture, platform, grouped_status
            FROM TEST_ROWS
            WHERE git_commit_hash = %(hash_b)s
        )
        SELECT
            COALESCE(a.path, b.path) AS path,
            COALESCE(a.config_name, b.config_name) AS config_name,
            COALESCE(a.architecture, b.architecture) AS architecture,
            COALESCE(a.platform, b.platform) AS platform,
            a.grouped_status AS status_a,
            b.grouped_status AS status_b
        FROM
            SIDE_A a
        FULL OUTER JOIN SIDE_B b ON (
            a.path = b.path
            AND a.config_name = b.config_name
            AND a.architecture = b.architecture
            AND a.platform = b.platform
        )
        WHERE
            (
                a.grouped_status IS DISTINCT FROM b.grouped_status
                OR (
                    a.grouped_status = 'FAIL'
                    AND b.grouped_status = 'FAIL'
                )
            )
            {filter_sql.post_join}
        ORDER BY
            1, 2, 3, 4
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = dict_fetchall(cursor)
        set_query_cache(key=cache_key, params=cache_params, rows=rows)
        return rows


def get_tree_commit_history(
    *,
    commit_hash: str,
    origin: str,
    git_url: Optional[str],
    git_branch: Optional[str],
    tree_name: Optional[str],
    include_types: Optional[list[str]] = None,
) -> Optional[list[tuple]]:
    if not include_types:
        include_types = ["builds", "boots", "tests"]

    include_types = [t.lower() for t in include_types]

    field_values = {
        "commit_hash": commit_hash,
        "origin_param": origin,
        "git_url_param": git_url,
        "git_branch_param": git_branch,
        "tree_name": tree_name,
    }

    checkout_clauses = create_checkouts_where_clauses(
        git_url=git_url, git_branch=git_branch, tree_name=tree_name
    )

    git_branch_clause = checkout_clauses.get("git_branch_clause")
    tree_name_clause = checkout_clauses.get("tree_name_clause")
    git_url_clause = checkout_clauses.get("git_url_clause")
    tree_name_full_clause = "AND " + tree_name_clause if tree_name_clause else ""
    git_url_full_clause = "AND " + git_url_clause if git_url_clause else ""

    selected_checkouts_clause = _create_selected_checkouts_clause(
        git_url=git_url, git_branch=git_branch, tree_name=tree_name
    )

    include_builds = "builds" in include_types
    include_boots = "boots" in include_types
    include_tests = "tests" in include_types
    include_test_data = include_tests or include_boots

    build_prefix = "b." if include_builds else "NULL AS "
    test_prefix = "t." if include_test_data else "NULL AS "
    build_id = "b.id" if include_builds else "NULL"
    build_misc = "b.misc" if include_builds else "NULL"
    # TODO remove misc fallbacks after lab backfill
    build_lab = "COALESCE(bl.name, b.misc->>'lab')" if include_builds else "NULL"
    test_misc_runtime = (
        "COALESCE(tl.name, t.misc->>'runtime')" if include_test_data else "NULL"
    )
    test_id = "t.id" if include_test_data else "NULL"

    select_clause = f"""c.git_commit_hash,
        c.git_commit_name,
        c.git_commit_tags,
        c.start_time,
        {build_prefix}duration,
        {build_prefix}architecture,
        {build_prefix}compiler,
        {build_prefix}config_name,
        {build_prefix}status,
        {build_prefix}origin,
        {build_id} AS build_id,
        {build_misc} AS build_misc,
        {test_prefix}path,
        {test_prefix}status,
        {test_prefix}duration,
        {test_prefix}environment_compatible,
        {test_prefix}environment_misc,
        {test_prefix}origin,
        {test_misc_runtime} AS test_lab,
        {test_id} AS test_id,
        ic.id AS incidents_id,
        ic.test_id AS incidents_test_id,
        i.id AS issues_id,
        i.version AS issues_version,
        {build_lab} AS build_lab"""

    if include_boots and not include_tests:
        test_filter = "AND (t.path IS NULL OR t.path LIKE 'boot%%')"
    elif include_tests and not include_boots:
        test_filter = "AND (t.path IS NULL OR t.path NOT LIKE 'boot%%')"
    else:
        test_filter = ""

    if include_test_data:
        test_join = f"LEFT JOIN tests AS t ON t.build_id = b.id {test_filter}"
        test_join += "\n        LEFT JOIN labs AS tl ON t.lab_id = tl.id"
        incidents_condition = "t.id = ic.test_id OR b.id = ic.build_id"
    else:
        test_join = ""
        incidents_condition = "b.id = ic.build_id"

    join_clause = f"""LEFT JOIN builds AS b ON c.id = b.checkout_id
        LEFT JOIN labs AS bl ON b.lab_id = bl.id
        {test_join}
        LEFT JOIN incidents AS ic ON {incidents_condition}
        LEFT JOIN issues AS i ON ic.issue_id = i.id"""

    query = f"""
    WITH HEAD_START_TIME AS (
        SELECT
            MAX(start_time) AS HEAD_START_TIME
        FROM
            checkouts
        WHERE
            (git_commit_hash = %(commit_hash)s
            OR %(commit_hash)s = ANY(checkouts.git_commit_tags))
            AND origin = %(origin_param)s
            AND {git_branch_clause}
            {git_url_full_clause}
            {tree_name_full_clause}
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
            tree_name,
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
                tree_name,
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
                {git_url_full_clause}
                {tree_name_full_clause}
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
        {select_clause}
    FROM
        SELECTED_CHECKOUTS AS c
        {join_clause}
    """

    with connection.cursor() as cursor:
        cursor.execute(query, field_values)
        return cursor.fetchall()


def get_latest_tree(
    *,
    tree_name: str,
    git_branch: str,
    origin: str,
    git_commit_hash: Optional[str] = None,
) -> Optional[dict]:
    """Retrieves the most recent occurrence of the checkout of a tree with the given params."""

    tree_fields = [
        "git_commit_hash",
        "git_commit_name",
        "git_repository_url",
        "git_repository_branch",
        "tree_name",
        "origin",
    ]

    query = Checkouts.objects.values(*tree_fields).filter(
        origin=origin,
        git_repository_branch=git_branch,
        tree_name=tree_name,
    )

    if git_commit_hash is not None:
        query = query.filter(
            Q(git_commit_hash=git_commit_hash)
            | Q(git_commit_tags__contains=[git_commit_hash])
        )
    else:
        query = query.filter(git_commit_hash__isnull=False)

    query = query.order_by("-start_time").first()

    return query


def _get_compare_checkout_clauses(
    *,
    git_branch_param: Optional[str],
    tree_name: Optional[str],
) -> tuple[str, str]:
    checkout_clauses = create_checkouts_where_clauses(
        git_url=None,
        git_branch=git_branch_param,
        tree_name=tree_name,
    )

    git_branch_clause = checkout_clauses.get("git_branch_clause")
    tree_name_clause = checkout_clauses.get("tree_name_clause")
    tree_name_full_clause = "AND " + tree_name_clause if tree_name_clause else ""

    return git_branch_clause, tree_name_full_clause


def get_tree_compare_rollup(
    *,
    commit_hashes: list[str],
    origin_param: str,
    git_branch_param: Optional[str],
    tree_name: Optional[str] = None,
) -> list[dict]:
    if not commit_hashes:
        return []

    cache_key = "treeCompareRollup"
    params = {
        "commit_hashes": commit_hashes,
        "tree_name": tree_name,
        "origin_param": origin_param,
        "git_branch_param": git_branch_param,
    }

    rows = get_query_cache(cache_key, params)
    if rows is not None:
        return rows

    git_branch_clause, tree_name_full_clause = _get_compare_checkout_clauses(
        git_branch_param=git_branch_param,
        tree_name=tree_name,
    )

    query = f"""
        WITH RELEVANT_CHECKOUTS AS (
            SELECT DISTINCT ON (c.git_commit_hash)
                c.git_commit_hash,
                c.tree_name,
                c.git_repository_branch,
                c.git_repository_url,
                c.origin
            FROM
                checkouts c
            WHERE
                c.git_commit_hash = ANY(%(commit_hashes)s)
                {tree_name_full_clause}
                AND {git_branch_clause}
                AND c.origin = %(origin_param)s
            ORDER BY
                c.git_commit_hash,
                c._timestamp DESC
        )
        SELECT
            tr.git_commit_hash,
            tr.path_group,
            tr.build_architecture,
            tr.hardware_key,
            tr.test_platform,
            tr.is_boot,
            tr.pass_tests,
            tr.fail_tests,
            tr.skip_tests,
            tr.error_tests,
            tr.miss_tests,
            tr.done_tests,
            tr.null_tests,
            tr.total_tests
        FROM
            tree_tests_rollup tr
        INNER JOIN RELEVANT_CHECKOUTS rc ON (
            tr.git_commit_hash = rc.git_commit_hash
            AND tr.origin = rc.origin
            AND tr.tree_name IS NOT DISTINCT FROM rc.tree_name
            AND tr.git_repository_branch IS NOT DISTINCT FROM rc.git_repository_branch
            AND tr.git_repository_url IS NOT DISTINCT FROM rc.git_repository_url
        )
        ORDER BY
            tr.total_tests DESC
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = dict_fetchall(cursor=cursor)
        set_query_cache(key=cache_key, params=params, rows=rows)

    return rows


def get_tree_compare_builds(
    *,
    commit_hashes: list[str],
    origin_param: str,
    git_branch_param: Optional[str],
    tree_name: Optional[str] = None,
) -> list[dict]:
    if not commit_hashes:
        return []

    cache_key = "treeCompareBuilds"
    params = {
        "commit_hashes": commit_hashes,
        "tree_name": tree_name,
        "origin_param": origin_param,
        "git_branch_param": git_branch_param,
    }

    rows = get_query_cache(cache_key, params)
    if rows is not None:
        return rows

    git_branch_clause, tree_name_full_clause = _get_compare_checkout_clauses(
        git_branch_param=git_branch_param,
        tree_name=tree_name,
    )

    query = f"""
        WITH RELEVANT_CHECKOUTS AS (
            SELECT DISTINCT ON (c.git_commit_hash)
                c.id AS checkout_id,
                c.git_commit_hash,
                c.git_repository_url
            FROM
                checkouts c
            WHERE
                c.git_commit_hash = ANY(%(commit_hashes)s)
                {tree_name_full_clause}
                AND {git_branch_clause}
                AND c.origin = %(origin_param)s
            ORDER BY
                c.git_commit_hash,
                c._timestamp DESC
        )
        SELECT
            rc.git_commit_hash,
            rc.git_repository_url,
            b.architecture,
            b.status,
            COUNT(DISTINCT b.id) AS count
        FROM
            RELEVANT_CHECKOUTS rc
        INNER JOIN builds b ON b.checkout_id = rc.checkout_id
        WHERE
            b.id NOT LIKE 'maestro:dummy_%%'
        GROUP BY
            rc.git_commit_hash,
            rc.git_repository_url,
            b.architecture,
            b.status
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = dict_fetchall(cursor=cursor)
        set_query_cache(key=cache_key, params=params, rows=rows)

    return rows


def get_tree_compare_builds_diff(
    *,
    hash_a: str,
    hash_b: str,
    origin_param: str,
    git_branch_param: Optional[str],
    tree_name: Optional[str] = None,
    filters: Optional["FilterParams"] = None,
) -> list[dict]:
    """Return build rows whose grouped status differs between two commits.

    Identity key: config_name + architecture + compiler.
    Statuses are bucketed to PASS / FAIL / INCONCLUSIVE before compare so
    SKIP vs MISS is not treated as a difference.

    Named *_diff to avoid colliding with get_tree_compare_builds (summary aggregates).
    """
    commit_hashes = [hash_a, hash_b]
    filter_sql = build_build_compare_filter_clauses(filters)

    cache_key = "treeCompareBuildsDiff"
    params = {
        "hash_a": hash_a,
        "hash_b": hash_b,
        "commit_hashes": commit_hashes,
        "tree_name": tree_name,
        "origin_param": origin_param,
        "git_branch_param": git_branch_param,
        "unknown_string": UNKNOWN_STRING,
        **filter_sql.params,
    }
    cache_params = {
        **params,
        "filter_pre_join": filter_sql.pre_join,
        "filter_post_join": filter_sql.post_join,
    }

    rows = get_query_cache(cache_key, cache_params)
    if rows is not None:
        return rows

    git_branch_clause, tree_name_full_clause = _get_compare_checkout_clauses(
        git_branch_param=git_branch_param,
        tree_name=tree_name,
    )

    query = f"""
        WITH RELEVANT_CHECKOUTS AS (
            SELECT DISTINCT ON (c.git_commit_hash)
                c.id AS checkout_id,
                c.git_commit_hash
            FROM
                checkouts c
            WHERE
                c.git_commit_hash = ANY(%(commit_hashes)s)
                {tree_name_full_clause}
                AND {git_branch_clause}
                AND c.origin = %(origin_param)s
            ORDER BY
                c.git_commit_hash,
                c._timestamp DESC
        ),
        BUILD_ROWS AS (
            SELECT DISTINCT ON (
                rc.git_commit_hash,
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.compiler, ''), %(unknown_string)s)
            )
                rc.git_commit_hash,
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s)
                    AS config_name,
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s)
                    AS architecture,
                COALESCE(NULLIF(b.compiler, ''), %(unknown_string)s) AS compiler,
                CASE
                    WHEN UPPER(b.status) = 'PASS' THEN 'PASS'
                    WHEN UPPER(b.status) = 'FAIL' THEN 'FAIL'
                    ELSE 'INCONCLUSIVE'
                END AS grouped_status
            FROM
                RELEVANT_CHECKOUTS rc
            INNER JOIN builds b ON b.checkout_id = rc.checkout_id
            WHERE
                b.id NOT LIKE 'maestro:dummy_%%'
                {filter_sql.pre_join}
            ORDER BY
                rc.git_commit_hash,
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.compiler, ''), %(unknown_string)s),
                b.start_time DESC NULLS LAST,
                b._timestamp DESC NULLS LAST
        ),
        SIDE_A AS (
            SELECT config_name, architecture, compiler, grouped_status
            FROM BUILD_ROWS
            WHERE git_commit_hash = %(hash_a)s
        ),
        SIDE_B AS (
            SELECT config_name, architecture, compiler, grouped_status
            FROM BUILD_ROWS
            WHERE git_commit_hash = %(hash_b)s
        )
        SELECT
            COALESCE(a.config_name, b.config_name) AS config_name,
            COALESCE(a.architecture, b.architecture) AS architecture,
            COALESCE(a.compiler, b.compiler) AS compiler,
            a.grouped_status AS status_a,
            b.grouped_status AS status_b
        FROM
            SIDE_A a
        FULL OUTER JOIN SIDE_B b ON (
            a.config_name = b.config_name
            AND a.architecture = b.architecture
            AND a.compiler = b.compiler
        )
        WHERE
            (
                a.grouped_status IS DISTINCT FROM b.grouped_status
                OR (
                    a.grouped_status = 'FAIL'
                    AND b.grouped_status = 'FAIL'
                )
            )
            {filter_sql.post_join}
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = dict_fetchall(cursor=cursor)
        set_query_cache(key=cache_key, params=cache_params, rows=rows)

    return rows


# Keep in sync with dashboard deriveCompareChange (INCONCLUSIVE transitions included).
_CHANGE_COUNT_SELECT = """
    COUNT(*) FILTER (
        WHERE status_a = 'PASS' AND status_b IN ('FAIL', 'INCONCLUSIVE')
    ) AS regression,
    COUNT(*) FILTER (
        WHERE status_a = 'FAIL' AND status_b IN ('PASS', 'INCONCLUSIVE')
    ) AS fixed,
    COUNT(*) FILTER (
        WHERE (status_a IS NULL OR status_a = 'INCONCLUSIVE')
          AND status_b = 'FAIL'
    ) AS new_failure,
    COUNT(*) FILTER (
        WHERE status_a = 'FAIL' AND status_b = 'FAIL'
    ) AS still_failing,
    COUNT(*) FILTER (
        WHERE (status_a IS NULL OR status_a = 'INCONCLUSIVE')
          AND status_b = 'PASS'
    ) AS new_pass,
    COUNT(*) FILTER (
        WHERE status_a IS NULL AND status_b = 'INCONCLUSIVE'
    ) AS appeared,
    COUNT(*) FILTER (
        WHERE status_a IS NOT NULL AND status_b IS NULL
    ) AS disappeared
"""


def _empty_change_counts() -> dict:
    return {
        "regression": 0,
        "fixed": 0,
        "new_failure": 0,
        "still_failing": 0,
        "new_pass": 0,
        "appeared": 0,
        "disappeared": 0,
    }


def get_tree_compare_builds_change_counts(
    *,
    hash_a: str,
    hash_b: str,
    origin_param: str,
    git_branch_param: Optional[str],
    tree_name: Optional[str] = None,
) -> dict:
    """Aggregate build A/B change categories (including still-failing)."""
    commit_hashes = [hash_a, hash_b]
    cache_key = "treeCompareBuildsChangeCounts"
    params = {
        "hash_a": hash_a,
        "hash_b": hash_b,
        "commit_hashes": commit_hashes,
        "tree_name": tree_name,
        "origin_param": origin_param,
        "git_branch_param": git_branch_param,
        "unknown_string": UNKNOWN_STRING,
    }

    cached = get_query_cache(cache_key, params)
    if cached is not None:
        return cached[0] if cached else _empty_change_counts()

    git_branch_clause, tree_name_full_clause = _get_compare_checkout_clauses(
        git_branch_param=git_branch_param,
        tree_name=tree_name,
    )

    query = f"""
        WITH RELEVANT_CHECKOUTS AS (
            SELECT DISTINCT ON (c.git_commit_hash)
                c.id AS checkout_id,
                c.git_commit_hash
            FROM
                checkouts c
            WHERE
                c.git_commit_hash = ANY(%(commit_hashes)s)
                {tree_name_full_clause}
                AND {git_branch_clause}
                AND c.origin = %(origin_param)s
            ORDER BY
                c.git_commit_hash,
                c._timestamp DESC
        ),
        BUILD_ROWS AS (
            SELECT DISTINCT ON (
                rc.git_commit_hash,
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.compiler, ''), %(unknown_string)s)
            )
                rc.git_commit_hash,
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s)
                    AS config_name,
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s)
                    AS architecture,
                COALESCE(NULLIF(b.compiler, ''), %(unknown_string)s) AS compiler,
                CASE
                    WHEN UPPER(b.status) = 'PASS' THEN 'PASS'
                    WHEN UPPER(b.status) = 'FAIL' THEN 'FAIL'
                    ELSE 'INCONCLUSIVE'
                END AS grouped_status
            FROM
                RELEVANT_CHECKOUTS rc
            INNER JOIN builds b ON b.checkout_id = rc.checkout_id
            WHERE
                b.id NOT LIKE 'maestro:dummy_%%'
            ORDER BY
                rc.git_commit_hash,
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.compiler, ''), %(unknown_string)s),
                b.start_time DESC NULLS LAST,
                b._timestamp DESC NULLS LAST
        ),
        SIDE_A AS (
            SELECT config_name, architecture, compiler, grouped_status
            FROM BUILD_ROWS
            WHERE git_commit_hash = %(hash_a)s
        ),
        SIDE_B AS (
            SELECT config_name, architecture, compiler, grouped_status
            FROM BUILD_ROWS
            WHERE git_commit_hash = %(hash_b)s
        ),
        PAIRED AS (
            SELECT
                a.grouped_status AS status_a,
                b.grouped_status AS status_b
            FROM
                SIDE_A a
            FULL OUTER JOIN SIDE_B b ON (
                a.config_name = b.config_name
                AND a.architecture = b.architecture
                AND a.compiler = b.compiler
            )
        )
        SELECT
            {_CHANGE_COUNT_SELECT}
        FROM
            PAIRED
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = dict_fetchall(cursor=cursor)
        set_query_cache(key=cache_key, params=params, rows=rows)

    return rows[0] if rows else _empty_change_counts()


def get_tree_compare_boots_change_counts(
    *,
    hash_a: str,
    hash_b: str,
    origin_param: str,
    git_branch_param: Optional[str],
    tree_name: Optional[str] = None,
) -> dict:
    """Aggregate boot A/B change categories (including still-failing)."""
    return _get_tree_compare_boots_tests_change_counts(
        data_type="boots",
        hash_a=hash_a,
        hash_b=hash_b,
        origin_param=origin_param,
        git_branch_param=git_branch_param,
        tree_name=tree_name,
    )


def get_tree_compare_tests_change_counts(
    *,
    hash_a: str,
    hash_b: str,
    origin_param: str,
    git_branch_param: Optional[str],
    tree_name: Optional[str] = None,
) -> dict:
    """Aggregate non-boot test A/B change categories (including still-failing)."""
    return _get_tree_compare_boots_tests_change_counts(
        data_type="tests",
        hash_a=hash_a,
        hash_b=hash_b,
        origin_param=origin_param,
        git_branch_param=git_branch_param,
        tree_name=tree_name,
    )


def _get_tree_compare_boots_tests_change_counts(
    *,
    data_type: Literal["boots", "tests"],
    hash_a: str,
    hash_b: str,
    origin_param: str,
    git_branch_param: Optional[str],
    tree_name: Optional[str] = None,
) -> dict:
    """Identity key matches get_tree_compare_boots_tests_diff: path+config+arch+platform."""
    commit_hashes = [hash_a, hash_b]
    cache_key = (
        "treeCompareBootsChangeCounts"
        if data_type == "boots"
        else "treeCompareTestsChangeCounts"
    )
    params = {
        "hash_a": hash_a,
        "hash_b": hash_b,
        "commit_hashes": commit_hashes,
        "tree_name": tree_name,
        "origin_param": origin_param,
        "git_branch_param": git_branch_param,
        "unknown_string": UNKNOWN_STRING,
    }

    cached = get_query_cache(cache_key, params)
    if cached is not None:
        return cached[0] if cached else _empty_change_counts()

    git_branch_clause, tree_name_full_clause = _get_compare_checkout_clauses(
        git_branch_param=git_branch_param,
        tree_name=tree_name,
    )

    if data_type == "boots":
        path_filter = "AND (t.path = 'boot' OR t.path LIKE 'boot.%%')"
    else:
        path_filter = "AND t.path IS DISTINCT FROM 'boot' AND t.path NOT LIKE 'boot.%%'"

    query = f"""
        WITH RELEVANT_CHECKOUTS AS (
            SELECT DISTINCT ON (c.git_commit_hash)
                c.id AS checkout_id,
                c.git_commit_hash
            FROM
                checkouts c
            WHERE
                c.git_commit_hash = ANY(%(commit_hashes)s)
                {tree_name_full_clause}
                AND {git_branch_clause}
                AND c.origin = %(origin_param)s
            ORDER BY
                c.git_commit_hash,
                c._timestamp DESC
        ),
        TEST_ROWS AS (
            SELECT DISTINCT ON (
                rc.git_commit_hash,
                COALESCE(NULLIF(t.path, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s),
                COALESCE(
                    NULLIF(t.environment_misc->>'platform', ''),
                    %(unknown_string)s
                )
            )
                rc.git_commit_hash,
                COALESCE(NULLIF(t.path, ''), %(unknown_string)s) AS path,
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s)
                    AS config_name,
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s)
                    AS architecture,
                COALESCE(
                    NULLIF(t.environment_misc->>'platform', ''),
                    %(unknown_string)s
                ) AS platform,
                CASE
                    WHEN UPPER(t.status) = 'PASS' THEN 'PASS'
                    WHEN UPPER(t.status) = 'FAIL' THEN 'FAIL'
                    ELSE 'INCONCLUSIVE'
                END AS grouped_status
            FROM
                RELEVANT_CHECKOUTS rc
            INNER JOIN builds b ON b.checkout_id = rc.checkout_id
            INNER JOIN tests t ON t.build_id = b.id
                {path_filter}
            WHERE
                b.id NOT LIKE 'maestro:dummy_%%'
            ORDER BY
                rc.git_commit_hash,
                COALESCE(NULLIF(t.path, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s),
                COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s),
                COALESCE(
                    NULLIF(t.environment_misc->>'platform', ''),
                    %(unknown_string)s
                ),
                t.start_time DESC NULLS LAST,
                t._timestamp DESC NULLS LAST
        ),
        SIDE_A AS (
            SELECT path, config_name, architecture, platform, grouped_status
            FROM TEST_ROWS
            WHERE git_commit_hash = %(hash_a)s
        ),
        SIDE_B AS (
            SELECT path, config_name, architecture, platform, grouped_status
            FROM TEST_ROWS
            WHERE git_commit_hash = %(hash_b)s
        ),
        PAIRED AS (
            SELECT
                a.grouped_status AS status_a,
                b.grouped_status AS status_b
            FROM
                SIDE_A a
            FULL OUTER JOIN SIDE_B b ON (
                a.path = b.path
                AND a.config_name = b.config_name
                AND a.architecture = b.architecture
                AND a.platform = b.platform
            )
        )
        SELECT
            {_CHANGE_COUNT_SELECT}
        FROM
            PAIRED
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = dict_fetchall(cursor=cursor)
        set_query_cache(key=cache_key, params=params, rows=rows)

    return rows[0] if rows else _empty_change_counts()
