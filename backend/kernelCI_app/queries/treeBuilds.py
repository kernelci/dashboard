"""Filtered, one-row-per-build data for the tree Builds endpoint."""

from typing import Any, Optional

from django.db import connection

from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.constants.general import (
    MAESTRO_DUMMY_BUILD_PREFIX,
    UNCATEGORIZED_STRING,
    UNKNOWN_STRING,
)
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.misc import handle_misc
from kernelCI_app.helpers.treeDetails import create_checkouts_where_clauses
from kernelCI_app.typeModels.commonDetails import BuildHistoryItem


def _filter_clauses(filters: FilterParams) -> tuple[str, str, dict[str, Any]]:
    """Keep the Builds tab's Python filter semantics, including nulls and ints."""
    params: dict[str, Any] = {
        "unknown": UNKNOWN_STRING,
        "uncategorized": UNCATEGORIZED_STRING,
        "dummy_prefix": MAESTRO_DUMMY_BUILD_PREFIX,
        "build_issue_filters": sorted(filters.filterIssues["build"], key=str),
    }
    clauses = ["left(b.id, length(%(dummy_prefix)s)) <> %(dummy_prefix)s"]
    for name, column, values in (
        (
            "architectures",
            "COALESCE(b.architecture, %(unknown)s)",
            filters.filterArchitecture,
        ),
        ("configs", "COALESCE(b.config_name, %(unknown)s)", filters.filterConfigs),
        ("compilers", "COALESCE(b.compiler, %(unknown)s)", filters.filterCompiler),
        ("statuses", "upper(COALESCE(b.status, 'NULL'))", filters.filterBuildStatus),
        ("origins", "b.origin", filters.filter_build_origin),
        (
            "labs",
            "COALESCE(NULLIF(COALESCE(l.name, b.misc->>'lab'), ''), %(unknown)s)",
            filters.filter_labs["build"],
        ),
        (
            "hardware",
            "CASE WHEN NOT COALESCE(b.misc ? 'platform', FALSE) THEN %(unknown)s "
            "WHEN jsonb_typeof(b.misc->'platform') = 'string' THEN b.misc->>'platform' END",
            filters.filterHardware,
        ),
    ):
        if values:
            params[name] = sorted(values)
            clauses.append(f"{column} = ANY(%({name})s)")

    for name, value, operator in (
        ("duration_min", filters.filterBuildDurationMin, ">="),
        ("duration_max", filters.filterBuildDurationMax, "<="),
    ):
        if value is not None:
            params[name] = value
            clauses.append(
                "b.duration IS NOT NULL AND "
                "(CASE WHEN b.duration = 'NaN'::float8 THEN 0 ELSE trunc(b.duration) END) "
                f"{operator} %({name})s"
            )

    issue_clauses = []
    for index, issue in enumerate(sorted(filters.filterIssues["build"], key=str)):
        if issue == UNCATEGORIZED_STRING:
            issue_clauses.append(
                "(effective_issue_id = %(uncategorized)s OR "
                "(i.test_id IS NOT NULL AND iss.id IS NOT NULL AND iss.version IS NOT NULL))"
            )
            continue
        issue_id, version = issue
        params[f"issue_id_{index}"] = issue_id
        params[f"issue_version_{index}"] = version
        issue_clauses.append(
            f"(effective_issue_id = %(issue_id_{index})s "
            f"AND iss.version IS NOT DISTINCT FROM %(issue_version_{index})s)"
        )
    issue_where = ""
    if issue_clauses:
        # Failure status is intentionally case-sensitive, like should_filter_build_issue.
        clauses.append("(b.status = 'FAIL' OR b.status IS NULL OR b.status = 'NULL')")
        clauses.append("selected_issue.matched IS TRUE")
        issue_where = "WHERE " + " OR ".join(issue_clauses)
    return " AND ".join(clauses), issue_where, params


def get_tree_builds_response(
    *,
    filters: FilterParams,
    origin: str,
    git_url: Optional[str],
    git_branch: Optional[str],
    commit_hash: str,
    tree_name: Optional[str],
) -> dict[str, Any]:
    where, issue_where, params = _filter_clauses(filters)
    params.update(
        origin=origin,
        git_url_param=git_url,
        git_branch_param=git_branch,
        commit_hash=commit_hash,
        tree_name=tree_name,
    )
    cache_key = "treeBuildsResponseV1"
    cached = get_query_cache(cache_key, params)
    if cached is not None:
        return cached

    checkout_filters = create_checkouts_where_clauses(git_url, git_branch, tree_name)
    checkout_where = " AND ".join(v for v in checkout_filters.values() if v)
    query = f"""
        WITH relevant_hash AS (
            SELECT git_commit_hash FROM checkouts
            WHERE git_commit_hash = %(commit_hash)s OR %(commit_hash)s = ANY(git_commit_tags)
            ORDER BY _timestamp DESC LIMIT 1
        ), relevant_checkouts AS MATERIALIZED (
            SELECT id, git_repository_url, git_repository_branch FROM checkouts
            WHERE git_commit_hash = (SELECT git_commit_hash FROM relevant_hash)
                AND origin = %(origin)s AND {checkout_where}
        ), metadata AS (
            SELECT count(*) AS checkout_count,
                EXISTS(SELECT 1 FROM relevant_checkouts c JOIN builds b ON b.checkout_id = c.id)
                    AS has_builds
            FROM relevant_checkouts
        ), filtered AS (
            SELECT b.id, b.origin, b.architecture, b.config_name, b.misc, b.config_url,
                b.compiler, b.status, b.duration, b.log_url, b.start_time,
                c.git_repository_url, c.git_repository_branch,
                COALESCE(l.name, b.misc->>'lab') AS lab,
                selected_issue.issue_timestamp
            FROM relevant_checkouts c JOIN builds b ON b.checkout_id = c.id
            LEFT JOIN labs l ON l.id = b.lab_id
            LEFT JOIN LATERAL (
                SELECT iss._timestamp AS issue_timestamp, TRUE AS matched
                FROM (SELECT 1) seed
                LEFT JOIN incidents i ON i.build_id = b.id
                LEFT JOIN issues iss ON iss.id = i.issue_id AND iss.version = i.issue_version
                CROSS JOIN LATERAL (
                    SELECT CASE WHEN iss.id IS NULL
                        OR (i.test_id IS NULL AND iss.version IS NULL)
                        OR (i.test_id IS NOT NULL AND iss.version IS NOT NULL)
                        THEN %(uncategorized)s ELSE iss.id END AS effective_issue_id
                ) identity
                {issue_where}
                ORDER BY iss._timestamp DESC LIMIT 1
            ) selected_issue ON TRUE
            WHERE {where}
        )
        SELECT metadata.checkout_count, metadata.has_builds,
            f.id, f.origin, f.architecture, f.config_name, f.misc, f.config_url,
            f.compiler, f.status, f.duration, f.log_url, f.start_time,
            f.git_repository_url, f.git_repository_branch, f.lab
        FROM metadata LEFT JOIN filtered f ON TRUE
        ORDER BY f.issue_timestamp DESC
    """
    builds = []
    error_message = None
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description][2:]
        for row in cursor:
            checkout_count, has_builds = row[:2]
            if not checkout_count:
                error_message = ClientStrings.TREE_NO_RESULTS
                break
            if checkout_count == 1 and not has_builds:
                error_message = ClientStrings.TREE_BUILDS_NO_RESULTS
                break
            if row[2] is None:
                continue
            item = dict(zip(columns, row[2:], strict=True))
            for field in ("architecture", "config_name", "compiler"):
                if item[field] is None:
                    item[field] = UNKNOWN_STRING
            item["lab"] = item["lab"] or UNKNOWN_STRING
            item["misc"] = handle_misc(item["misc"])
            builds.append(BuildHistoryItem.model_validate(item).model_dump())
    response = {"error": error_message} if error_message else {"builds": builds}
    set_query_cache(key=cache_key, params=params, rows=response)
    return response
