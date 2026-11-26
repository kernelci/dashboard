import json

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
    only_boots: bool = False,
) -> list[dict]:
    params = {
        "lab_name": lab_name,
        "origin": origin,
        "interval": f"{interval_in_days} days",
        **_tree_filter_params(tree_filters),
    }
    boot_sql = ""
    if only_boots:
        boot_sql = "AND (t.path = 'boot' OR t.path LIKE 'boot.%%')"
    query = f"""
        SELECT
            t.id AS test_id,
            t.status AS test_status,
            t.path AS test_path,
            t.start_time AS test_start_time,
            t.duration AS test_duration,
            t.log_url AS test_log_url,
            (t.log_excerpt IS NOT NULL AND t.log_excerpt <> '') AS test_has_log_excerpt,
            COALESCE(t.environment_misc->>'platform', '') AS test_platform,
            b.config_name AS build_config_name,
            b.architecture AS build_architecture,
            b.compiler AS build_compiler,
            c.tree_name AS tree_name,
            c.git_repository_branch AS git_branch,
            c.git_commit_hash AS commit_hash,
            c.git_commit_name AS commit_name
        FROM tests t
        INNER JOIN labs tl ON t.lab_id = tl.id AND tl.name = %(lab_name)s
        INNER JOIN builds b ON t.build_id = b.id
        INNER JOIN checkouts c ON b.checkout_id = c.id
        WHERE
            t.origin = %(origin)s
            AND t.start_time >= NOW() - INTERVAL %(interval)s
            AND t.path IS NOT NULL
            {boot_sql}
            {_TREE_FILTER_SQL}
        ORDER BY t.start_time DESC NULLS LAST
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor=cursor)


def _json(value):
    if value is None:
        return None
    return json.loads(value) if isinstance(value, str) else value


def get_lab_test_summary(
    *,
    lab_name: str,
    origin: str,
    interval_in_days: int,
) -> dict:
    params = {
        "lab_name": lab_name,
        "origin": origin,
        "interval": f"{interval_in_days} days",
    }
    # tests_in is materialized so every aggregate below shares that one scan.
    query = """
        WITH tests_in AS MATERIALIZED (
            SELECT
                t.id,
                t.status,
                t.start_time,
                (t.duration IS NOT NULL) AS has_duration,
                (t.log_url IS NOT NULL AND t.log_url <> '') AS has_log,
                (t.log_excerpt IS NOT NULL AND t.log_excerpt <> '') AS has_excerpt,
                BTRIM(COALESCE(t.environment_misc->>'platform', '')) AS platform,
                t.build_id,
                (t.path = 'boot' OR t.path LIKE 'boot.%%') AS is_boot
            FROM tests t
            INNER JOIN labs tl ON t.lab_id = tl.id AND tl.name = %(lab_name)s
            WHERE t.origin = %(origin)s
              AND t.start_time >= NOW() - INTERVAL %(interval)s
              AND t.path IS NOT NULL
        ),
        build_info AS (
            SELECT
                b.id AS build_id,
                BTRIM(COALESCE(b.config_name, '')) AS config_name,
                BTRIM(COALESCE(b.architecture, '')) AS architecture,
                BTRIM(COALESCE(b.compiler, '')) AS compiler,
                c.tree_name,
                c.git_repository_branch AS git_branch,
                c.git_commit_hash AS commit_hash,
                c.git_commit_name AS commit_name
            FROM (SELECT DISTINCT build_id FROM tests_in) ids
            INNER JOIN builds b ON b.id = ids.build_id
            INNER JOIN checkouts c ON c.id = b.checkout_id
        ),
        joined AS MATERIALIZED (
            SELECT
                t.id,
                t.status,
                t.start_time,
                t.has_duration,
                t.has_log,
                t.has_excerpt,
                t.platform,
                t.is_boot,
                bi.config_name,
                bi.architecture,
                bi.compiler,
                bi.tree_name,
                bi.git_branch,
                bi.commit_hash,
                bi.commit_name
            FROM tests_in t
            INNER JOIN build_info bi ON bi.build_id = t.build_id
        )
        SELECT
            COALESCE((
                SELECT jsonb_agg(jsonb_build_object(
                    'tree_name', tree_name,
                    'git_branch', git_branch,
                    'is_boot', is_boot,
                    'status', status,
                    'day', day,
                    'n', n
                ))
                FROM (
                    SELECT
                        tree_name, git_branch, is_boot, status,
                        start_time::date AS day, COUNT(*)::int AS n
                    FROM joined
                    GROUP BY 1, 2, 3, 4, 5
                ) s
            ), '[]'::jsonb) AS statuses,
            COALESCE((
                SELECT jsonb_agg(jsonb_build_object(
                    'tree_name', tree_name,
                    'git_branch', git_branch,
                    'commit_hash', commit_hash,
                    'commit_name', commit_name,
                    'at', start_time
                ))
                FROM (
                    SELECT DISTINCT ON (tree_name, git_branch)
                        tree_name, git_branch, commit_hash, commit_name, start_time
                    FROM joined
                    WHERE commit_hash IS NOT NULL AND start_time IS NOT NULL
                    ORDER BY tree_name, git_branch, start_time DESC
                ) latest
            ), '[]'::jsonb) AS commits,
            (
                SELECT jsonb_build_object(
                    'total', COUNT(*)::int,
                    'duration', COUNT(*) FILTER (WHERE has_duration)::int,
                    'platform', COUNT(*) FILTER (WHERE platform <> '')::int,
                    'log_url', COUNT(*) FILTER (WHERE has_log)::int,
                    'excerpt', COUNT(*) FILTER (WHERE has_excerpt)::int
                )
                FROM joined
            ) AS fill,
            COALESCE((
                SELECT jsonb_agg(jsonb_build_object('name', platform, 'n', n))
                FROM (
                    SELECT platform, COUNT(*)::int AS n FROM joined GROUP BY platform
                ) p
            ), '[]'::jsonb) AS platforms,
            COALESCE((
                SELECT jsonb_agg(jsonb_build_object('name', config_name, 'n', n))
                FROM (
                    SELECT config_name, COUNT(*)::int AS n
                    FROM joined GROUP BY config_name
                ) c
            ), '[]'::jsonb) AS configs,
            COALESCE((
                SELECT jsonb_agg(jsonb_build_object('name', compiler, 'n', n))
                FROM (
                    SELECT compiler, COUNT(*)::int AS n FROM joined GROUP BY compiler
                ) c
            ), '[]'::jsonb) AS compilers,
            COALESCE((
                SELECT jsonb_agg(jsonb_build_object('name', architecture, 'n', n))
                FROM (
                    SELECT architecture, COUNT(*)::int AS n
                    FROM joined GROUP BY architecture
                ) a
            ), '[]'::jsonb) AS architectures,
            COALESCE((
                SELECT jsonb_agg(jsonb_build_object(
                    'tree_name', tree_name,
                    'git_branch', git_branch,
                    'is_boot', is_boot,
                    'status', status,
                    'n', n,
                    'issue_id', issue_id,
                    'issue_version', issue_version,
                    'issue_comment', issue_comment,
                    'issue_report_url', issue_report_url
                ))
                FROM (
                    SELECT
                        j.tree_name, j.git_branch, j.is_boot, j.status,
                        COUNT(*)::int AS n,
                        iss.id AS issue_id, iss.version AS issue_version,
                        iss.comment AS issue_comment, iss.report_url AS issue_report_url
                    FROM joined j
                    INNER JOIN incidents inc ON inc.test_id = j.id
                    INNER JOIN issues iss
                        ON iss.id = inc.issue_id AND iss.version = inc.issue_version
                    GROUP BY 1, 2, 3, 4, 6, 7, 8, 9
                ) i
            ), '[]'::jsonb) AS issues
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        row = dict_fetchall(cursor=cursor)[0]
    return {
        "statuses": _json(row["statuses"]) or [],
        "commits": _json(row["commits"]) or [],
        "fill": _json(row["fill"]) or {},
        "platforms": _json(row["platforms"]) or [],
        "configs": _json(row["configs"]) or [],
        "compilers": _json(row["compilers"]) or [],
        "architectures": _json(row["architectures"]) or [],
        "issues": _json(row["issues"]) or [],
    }


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
    # passes is one lookup of the sibling builds, not one lookup per failure.
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
        ),
        passes AS MATERIALIZED (
            SELECT
                sb.tree_name,
                sb.git_branch,
                sb.commit_hash,
                sb.config_name,
                COALESCE(t.environment_misc->>'platform', '') AS platform,
                CASE
                    WHEN t.path = 'boot' OR t.path LIKE 'boot.%%' THEN 'boot'
                    ELSE 'test'
                END AS kind,
                CASE
                    WHEN t.path = 'boot' OR t.path LIKE 'boot.%%' THEN NULL
                    ELSE t.path
                END AS path,
                ARRAY_AGG(DISTINCT pl.name) AS passed_labs
            FROM sibling_builds sb
            INNER JOIN tests t ON t.build_id = sb.id
            INNER JOIN labs pl ON pl.id = t.lab_id AND pl.name <> %(lab_name)s
            WHERE t.status = 'PASS'
              AND t.origin = %(origin)s
            GROUP BY 1, 2, 3, 4, 5, 6, 7
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
        INNER JOIN passes p
            ON p.tree_name = f.tree_name
           AND p.git_branch = f.git_branch
           AND p.commit_hash = f.commit_hash
           AND p.platform = f.platform
           AND p.kind = f.kind
           AND p.config_name IS NOT DISTINCT FROM (
               CASE WHEN f.kind = 'boot' THEN NULL ELSE f.config_name END
           )
           AND (f.kind = 'boot' OR p.path IS NOT DISTINCT FROM f.path)
        ORDER BY f.last_failure_time DESC
        LIMIT %(limit)s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor=cursor)
