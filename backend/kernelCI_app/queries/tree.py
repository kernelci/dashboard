from django.db import connection

from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.helpers.treeDetails import create_checkouts_where_clauses


def get_tree_details_data(request, commit_hash: str) -> list[tuple]:
    cache_key = "treeDetails"

    origin_param = request.GET.get("origin")
    git_url_param = request.GET.get("git_url")
    git_branch_param = request.GET.get("git_branch")

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
                    builds.valid AS builds_valid,
                    builds.misc AS builds_misc,
                    tree_head.*
                FROM
                    (
                        SELECT
                            checkouts.id AS checkout_id,
                            checkouts.git_repository_url AS checkouts_git_repository_url,
                            checkouts.git_repository_branch AS checkouts_git_repository_branch,
                            checkouts.git_commit_tags
                        FROM
                            checkouts
                        WHERE
                            checkouts.git_commit_hash = %(commit_hash)s AND
                            {git_url_clause} AND
                            {git_branch_clause} AND
                            checkouts.origin = %(origin_param)s
                    ) AS tree_head
                INNER JOIN builds
                    ON tree_head.checkout_id = builds.checkout_id
                WHERE
                    builds.origin = %(origin_param)s
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
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            set_query_cache(cache_key, params, rows)

    return rows
