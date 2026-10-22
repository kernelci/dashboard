from django.db import connection

from kernelCI_app.helpers.database import dict_fetchall

_TREE_FILTER_SQL = """
    AND (
        %(tree_filter_enabled)s = FALSE
        OR (c.tree_name || '/' || c.git_repository_branch) = ANY(%(tree_keys)s)
    )
"""


def _tree_filter_params(
    tree_filters: set[tuple[str, str]] | None,
) -> dict:
    if not tree_filters:
        return {
            "tree_filter_enabled": False,
            "tree_keys": [],
        }
    return {
        "tree_filter_enabled": True,
        "tree_keys": [f"{tree}/{branch}" for tree, branch in sorted(tree_filters)],
    }


def get_lab_build_rows(
    *,
    lab_name: str,
    origin: str,
    interval_in_days: int,
    tree_filters: set[tuple[str, str]] | None = None,
) -> list[dict]:
    params = {
        "lab_name": lab_name,
        "origin": origin,
        "interval": f"{interval_in_days} days",
        **_tree_filter_params(tree_filters),
    }
    query = f"""
        SELECT
            b.id AS build_id,
            b.status AS build_status,
            b.start_time AS build_start_time,
            b.duration AS build_duration,
            b.architecture AS build_architecture,
            b.compiler AS build_compiler,
            b.config_name AS build_config_name,
            b.log_url AS build_log_url,
            b.log_excerpt AS build_log_excerpt,
            c.tree_name AS tree_name,
            c.git_repository_branch AS git_branch,
            c.git_commit_hash AS commit_hash,
            c.git_commit_name AS commit_name,
            inc.test_id AS incident_test_id,
            iss.id AS issue_id,
            iss.version AS issue_version,
            iss.comment AS issue_comment,
            iss.report_url AS issue_report_url
        FROM builds b
        INNER JOIN labs bl ON b.lab_id = bl.id AND bl.name = %(lab_name)s
        INNER JOIN checkouts c ON b.checkout_id = c.id
        LEFT JOIN incidents inc
            ON inc.build_id = b.id AND inc.test_id IS NULL
        LEFT JOIN issues iss
            ON inc.issue_id = iss.id AND inc.issue_version = iss.version
        WHERE
            b.origin = %(origin)s
            AND b.start_time >= NOW() - INTERVAL %(interval)s
            AND b.id NOT LIKE 'maestro:dummy_%%'
            {_TREE_FILTER_SQL}
        ORDER BY b.start_time DESC NULLS LAST
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor=cursor)


def get_lab_test_rows(
    *,
    lab_name: str,
    origin: str,
    interval_in_days: int,
    tree_filters: set[tuple[str, str]] | None = None,
) -> list[dict]:
    params = {
        "lab_name": lab_name,
        "origin": origin,
        "interval": f"{interval_in_days} days",
        **_tree_filter_params(tree_filters),
    }
    query = f"""
        SELECT
            t.id AS test_id,
            t.status AS test_status,
            t.path AS test_path,
            t.start_time AS test_start_time,
            t.duration AS test_duration,
            t.log_url AS test_log_url,
            t.log_excerpt AS test_log_excerpt,
            t.environment_misc AS test_environment_misc,
            b.config_name AS build_config_name,
            b.architecture AS build_architecture,
            b.compiler AS build_compiler,
            c.tree_name AS tree_name,
            c.git_repository_branch AS git_branch,
            c.git_commit_hash AS commit_hash,
            c.git_commit_name AS commit_name,
            inc.test_id AS incident_test_id,
            iss.id AS issue_id,
            iss.version AS issue_version,
            iss.comment AS issue_comment,
            iss.report_url AS issue_report_url
        FROM tests t
        INNER JOIN labs tl ON t.lab_id = tl.id AND tl.name = %(lab_name)s
        INNER JOIN builds b ON t.build_id = b.id
        INNER JOIN checkouts c ON b.checkout_id = c.id
        LEFT JOIN incidents inc ON inc.test_id = t.id
        LEFT JOIN issues iss
            ON inc.issue_id = iss.id AND inc.issue_version = iss.version
        WHERE
            t.origin = %(origin)s
            AND t.start_time >= NOW() - INTERVAL %(interval)s
            AND t.path IS NOT NULL
            {_TREE_FILTER_SQL}
        ORDER BY t.start_time DESC NULLS LAST
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor=cursor)


def get_lab_attention_items(
    *,
    lab_name: str,
    origin: str,
    interval_in_days: int,
    limit: int = 25,
) -> list[dict]:
    params = {
        "lab_name": lab_name,
        "origin": origin,
        "interval": f"{interval_in_days} days",
        "limit": limit,
    }
    # MATERIALIZED: sibling_builds is referenced once, so Postgres would inline
    # it and repeat the checkout walk for every failure.
    query = """
        WITH fails AS (
            SELECT
                CASE
                    WHEN f.path = 'boot' OR f.path LIKE 'boot.%%' THEN 'boot'
                    ELSE 'test'
                END AS kind,
                f.path,
                COALESCE(f.environment_misc->>'platform', '') AS platform,
                c.tree_name,
                c.git_repository_branch AS git_branch,
                c.git_commit_hash AS commit_hash,
                c.git_commit_name AS commit_name,
                b.config_name,
                b.architecture,
                b.compiler,
                MAX(f.start_time) AS last_failure_time
            FROM tests f
            INNER JOIN labs fl ON fl.id = f.lab_id AND fl.name = %(lab_name)s
            INNER JOIN builds b ON b.id = f.build_id
            INNER JOIN checkouts c ON c.id = b.checkout_id
            WHERE f.origin = %(origin)s
              AND f.status = 'FAIL'
              AND f.start_time >= NOW() - INTERVAL %(interval)s
              AND f.path IS NOT NULL
            GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
        ),
        sibling_builds AS MATERIALIZED (
            SELECT DISTINCT
                k.tree_name,
                k.git_branch,
                k.commit_hash,
                k.config_name,
                ob.id
            FROM (
                SELECT DISTINCT
                    tree_name,
                    git_branch,
                    commit_hash,
                    CASE WHEN kind = 'boot' THEN NULL ELSE config_name END AS config_name
                FROM fails
            ) k
            INNER JOIN checkouts oc
                ON oc.git_commit_hash = k.commit_hash
               AND oc.tree_name = k.tree_name
               AND oc.git_repository_branch = k.git_branch
            INNER JOIN builds ob
                ON ob.checkout_id = oc.id
               AND (k.config_name IS NULL OR ob.config_name = k.config_name)
        )
        SELECT
            f.kind,
            f.path,
            f.platform,
            f.tree_name,
            f.git_branch,
            f.commit_hash,
            f.commit_name,
            f.config_name,
            f.architecture,
            f.compiler,
            f.last_failure_time::date AS last_failure_date,
            p.passed_labs
        FROM fails f
        INNER JOIN LATERAL (
            SELECT ARRAY_AGG(DISTINCT pl.name) AS passed_labs
            FROM sibling_builds sb
            INNER JOIN tests t ON t.build_id = sb.id
            INNER JOIN labs pl ON pl.id = t.lab_id AND pl.name <> %(lab_name)s
            WHERE sb.tree_name = f.tree_name
              AND sb.git_branch = f.git_branch
              AND sb.commit_hash = f.commit_hash
              AND sb.config_name IS NOT DISTINCT FROM (
                  CASE WHEN f.kind = 'boot' THEN NULL ELSE f.config_name END
              )
              AND t.status = 'PASS'
              AND t.origin = %(origin)s
              AND COALESCE(t.environment_misc->>'platform', '') = f.platform
              AND (
                  (f.kind = 'test' AND t.path IS NOT DISTINCT FROM f.path)
                  OR (f.kind = 'boot' AND (t.path = 'boot' OR t.path LIKE 'boot.%%'))
              )
        ) p ON p.passed_labs IS NOT NULL
        ORDER BY f.last_failure_time DESC
        LIMIT %(limit)s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor=cursor)
