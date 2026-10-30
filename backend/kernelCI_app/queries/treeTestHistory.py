"""SQL-filtered tree test history, cached in its final response shape."""

from typing import Any, Literal, Optional

from django.db import connection

from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.constants.general import UNCATEGORIZED_STRING, UNKNOWN_STRING
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.labFilter import lab_filter_sql
from kernelCI_app.helpers.misc import handle_misc
from kernelCI_app.helpers.treeDetails import create_checkouts_where_clauses
from kernelCI_app.typeModels.commonDetails import TestHistoryItem


def _filter_clauses(  # noqa: C901 - maps FilterParams fields to SQL AND clauses
    filters: FilterParams, data_type: Literal["boots", "tests"]
) -> tuple[str, str, dict[str, Any]]:
    tab = "boot" if data_type == "boots" else "test"
    prefix = "Boot" if data_type == "boots" else "Test"
    params: dict[str, Any] = {
        "unknown": UNKNOWN_STRING,
        "uncategorized": UNCATEGORIZED_STRING,
    }
    build_platform = (
        "CASE WHEN NOT COALESCE(b.misc ? 'platform', FALSE) THEN %(unknown)s "
        "WHEN jsonb_typeof(b.misc->'platform') = 'string' THEN b.misc->>'platform' END"
    )
    test_platform = (
        "CASE WHEN jsonb_typeof(t.environment_misc->'platform') = 'string' "
        "THEN t.environment_misc->>'platform' END"
    )
    hardware = (
        "CASE WHEN t.environment_compatible IS NOT NULL "
        "AND t.environment_compatible[1] IS DISTINCT FROM %(unknown)s "
        "THEN t.environment_compatible[1] "
        "WHEN COALESCE(t.environment_misc ? 'platform', FALSE) "
        "AND t.environment_misc->'platform' IS DISTINCT FROM to_jsonb(%(unknown)s::text) "
        f"THEN {test_platform} ELSE {build_platform} END"
    )
    clauses = [
        "(t.path = 'boot' OR t.path LIKE 'boot.%%')"
        if data_type == "boots"
        else "(t.path <> 'boot' AND t.path NOT LIKE 'boot.%%')"
    ]
    for name, column, values in (
        (
            "architectures",
            "COALESCE(b.architecture, %(unknown)s)",
            filters.filterArchitecture,
        ),
        ("compilers", "COALESCE(b.compiler, %(unknown)s)", filters.filterCompiler),
        ("configs", "COALESCE(b.config_name, %(unknown)s)", filters.filterConfigs),
        ("hardware", hardware, filters.filterHardware),
        (
            "statuses",
            "COALESCE(t.status, 'NULL')",
            getattr(filters, f"filter{prefix}Status"),
        ),
        ("origins", "t.origin", getattr(filters, f"filter_{tab}_origin")),
    ):
        if values:
            params[name] = sorted(values)
            clauses.append(f"({column}) = ANY(%({name})s)")
    lab_sql, lab_params = lab_filter_sql(
        filters.filter_labs[tab], lab_id_column="t.lab_id", param="labs"
    )
    if lab_sql:
        clauses.append(lab_sql)
        params.update(lab_params)
    if getattr(filters, f"filter{prefix}Path"):
        params["path"] = getattr(filters, f"filter{prefix}Path")
        clauses.append("strpos(t.path, %(path)s) > 0")
    if filters.filterPlatforms[tab]:
        # The existing views pass no platform to their tab filter (None).
        params["platforms"] = sorted(filters.filterPlatforms[tab])
        clauses.append("FALSE")
    for name, value, operator in (
        ("duration_min", getattr(filters, f"filter{prefix}DurationMin"), ">="),
        ("duration_max", getattr(filters, f"filter{prefix}DurationMax"), "<="),
    ):
        if value is not None:
            params[name] = value
            clauses.append(
                "t.duration IS NOT NULL AND "
                "(CASE WHEN t.duration = 'NaN'::float8 THEN 0 ELSE trunc(t.duration) END) "
                f"{operator} %({name})s"
            )
    issues = sorted(filters.filterIssues[tab], key=str)
    params["issues"] = issues
    issue_clauses = []
    for index, issue in enumerate(issues):
        if issue == UNCATEGORIZED_STRING:
            issue_clauses.append("effective_issue_id = %(uncategorized)s")
        else:
            params[f"issue_id_{index}"], params[f"issue_version_{index}"] = issue
            issue_clauses.append(
                f"(effective_issue_id = %(issue_id_{index})s "
                f"AND iss.version IS NOT DISTINCT FROM %(issue_version_{index})s)"
            )
    issue_where = ""
    if issue_clauses:
        clauses.append("selected_issue.matched IS TRUE")
        issue_where = "WHERE " + " OR ".join(issue_clauses)
    return " AND ".join(clauses), issue_where, params


def get_tree_test_history_response(
    *,
    data_type: Literal["boots", "tests"],
    filters: FilterParams,
    origin: str,
    git_url: Optional[str],
    git_branch: Optional[str],
    commit_hash: str,
    tree_name: Optional[str],
    full_environment_misc: bool = False,
) -> dict[str, Any]:
    where, issue_where, params = _filter_clauses(filters, data_type)
    params.update(
        origin=origin,
        git_url_param=git_url,
        git_branch_param=git_branch,
        commit_hash=commit_hash,
        tree_name=tree_name,
        full_environment_misc=full_environment_misc,
    )
    cache_key = f"tree{data_type.capitalize()}ResponseV2"
    response = get_query_cache(cache_key, params)
    if response is not None:
        return response
    checkout_filters = create_checkouts_where_clauses(git_url, git_branch, tree_name)
    checkout_where = " AND ".join(v for v in checkout_filters.values() if v)
    environment_misc = (
        "t.environment_misc"
        if full_environment_misc
        else "jsonb_build_object('platform', CASE WHEN COALESCE(t.environment_misc ? 'platform', FALSE) "
        "THEN t.environment_misc->'platform' ELSE to_jsonb(%(unknown)s::text) END)"
    )
    query = f"""
        WITH relevant_hash AS (
            SELECT git_commit_hash FROM checkouts
            WHERE git_commit_hash = %(commit_hash)s OR %(commit_hash)s = ANY(git_commit_tags)
            ORDER BY _timestamp DESC LIMIT 1
        ), relevant_checkouts AS MATERIALIZED (
            SELECT id FROM checkouts
            WHERE git_commit_hash = (SELECT git_commit_hash FROM relevant_hash)
                AND origin = %(origin)s AND {checkout_where}
        ), filtered AS (
            SELECT t.id, t.origin, COALESCE(t.status, 'NULL') AS status, t.duration,
                t.path, t.start_time, t.environment_compatible,
                COALESCE(b.config_name, %(unknown)s) AS config, t.log_url,
                COALESCE(b.architecture, %(unknown)s) AS architecture,
                COALESCE(b.compiler, %(unknown)s) AS compiler,
                {environment_misc} AS environment_misc,
                COALESCE(NULLIF(COALESCE(tl.name, t.misc->>'runtime'), ''), %(unknown)s) AS lab,
                selected_issue.issue_timestamp
            FROM relevant_checkouts c JOIN builds b ON b.checkout_id = c.id
            JOIN tests t ON t.build_id = b.id
            LEFT JOIN labs tl ON tl.id = t.lab_id
            LEFT JOIN LATERAL (
                SELECT iss._timestamp AS issue_timestamp, TRUE AS matched
                FROM (SELECT 1) seed
                LEFT JOIN incidents i ON i.test_id = t.id
                LEFT JOIN issues iss ON iss.id = i.issue_id AND iss.version = i.issue_version
                CROSS JOIN LATERAL (
                    SELECT CASE WHEN iss.id IS NULL AND (
                        b.status IS NULL OR b.status IN ('FAIL', 'NULL') OR t.status = 'FAIL'
                    ) THEN %(uncategorized)s ELSE iss.id END AS effective_issue_id
                ) identity
                {issue_where}
                ORDER BY iss._timestamp DESC LIMIT 1
            ) selected_issue ON TRUE
            WHERE {where}
        )
        SELECT metadata.has_checkout, f.id, f.origin, f.status, f.duration, f.path,
            f.start_time, f.environment_compatible, f.config, f.log_url,
            f.architecture, f.compiler, f.environment_misc, f.lab
        FROM (SELECT EXISTS(SELECT 1 FROM relevant_checkouts) AS has_checkout) metadata
        LEFT JOIN filtered f ON TRUE ORDER BY f.issue_timestamp DESC
    """
    items = []
    error_message = None
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description][1:]
        for row in cursor:
            if not row[0]:
                error_message = ClientStrings.TREE_NO_RESULTS
                break
            if row[1] is None:
                continue
            item = dict(zip(columns, row[1:], strict=True))
            item["environment_misc"] = handle_misc(item["environment_misc"])
            if item["environment_misc"] is None:
                item["environment_misc"] = {"platform": UNKNOWN_STRING}
            items.append(TestHistoryItem.model_validate(item).model_dump())
    response = {"error": error_message} if error_message else {data_type: items}
    set_query_cache(key=cache_key, params=params, rows=response)
    return response
