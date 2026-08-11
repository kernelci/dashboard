from dataclasses import dataclass, field
from typing import Literal, Optional

from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.constants.process_pending import ROLLUP_STATUS_FIELDS
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.typeModels.databases import NULL_STATUS
from kernelCI_app.typeModels.treeCompare import (
    CompareChangeCounts,
    CompareDelta,
    CompareEntitySummary,
    CompareStatusCounts,
    CompareSummary,
    TreeCompareResponse,
)

BucketKey = Literal["pass", "fail", "inconclusive"]


@dataclass(frozen=True)
class CompareFilterSql:
    """Identity dims are safe pre-join; status must be applied after the A/B pair."""

    pre_join: str = ""
    post_join: str = ""
    params: dict = field(default_factory=dict)


def _to_grouped_status_filters(statuses: set[str]) -> list[str]:
    """Map raw FilterParams statuses onto compare PASS/FAIL/INCONCLUSIVE buckets."""
    grouped: set[str] = set()
    for status in statuses:
        if status == NULL_STATUS:
            grouped.add("INCONCLUSIVE")
            continue
        upper = status.upper()
        if upper == "PASS":
            grouped.add("PASS")
        elif upper == "FAIL":
            grouped.add("FAIL")
        else:
            grouped.add("INCONCLUSIVE")
    return list(grouped)


def _post_join_status_clause(
    statuses: set[str],
    *,
    param_key: str,
    params: dict,
) -> str:
    grouped = _to_grouped_status_filters(statuses)
    if not grouped:
        return ""
    params[param_key] = grouped
    return (
        f"AND (a.grouped_status = ANY(%({param_key})s)"
        f" OR b.grouped_status = ANY(%({param_key})s))"
    )


def build_build_compare_filter_clauses(  # noqa: C901 - maps FilterParams fields to SQL AND clauses
    filters: Optional["FilterParams"],
) -> CompareFilterSql:
    """Build compare filters for builds.

    Identity filters (config/arch/compiler/…) apply before the A/B join.
    Status filters apply after pairing so PASS→FAIL is not rewritten as newFailure.
    Duration/issue filters are skipped on compare: they need per-side columns we
    do not select on the paired row (ponytail: wire post-join when those land).
    """
    if filters is None:
        return CompareFilterSql()

    pre_join: list[str] = []
    params: dict = {}

    if filters.filter_build_origin:
        pre_join.append("AND b.origin = ANY(%(build_origins)s)")
        params["build_origins"] = list(filters.filter_build_origin)

    if filters.filterConfigs:
        pre_join.append(
            "AND COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s)"
            " = ANY(%(configs)s)"
        )
        params["configs"] = list(filters.filterConfigs)
        params["unknown_string"] = UNKNOWN_STRING

    if filters.filterArchitecture:
        pre_join.append(
            "AND COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s)"
            " = ANY(%(architectures)s)"
        )
        params["architectures"] = list(filters.filterArchitecture)
        params["unknown_string"] = UNKNOWN_STRING

    if filters.filterCompiler:
        pre_join.append(
            "AND COALESCE(NULLIF(b.compiler, ''), %(unknown_string)s)"
            " = ANY(%(compilers)s)"
        )
        params["compilers"] = list(filters.filterCompiler)
        params["unknown_string"] = UNKNOWN_STRING

    if filters.filter_labs:
        pre_join.append(
            "AND COALESCE(NULLIF(b.misc->>'lab', ''), %(unknown_string)s)"
            " = ANY(%(labs)s)"
        )
        params["labs"] = list(filters.filter_labs)
        params["unknown_string"] = UNKNOWN_STRING

    if filters.filterHardware:
        # Keep hardware filter as EXISTS so we don't multiply build rows by tests
        pre_join.append(
            """
            AND EXISTS (
                SELECT 1 FROM tests ht
                WHERE ht.build_id = b.id
                  AND (
                    ht.environment_compatible && %(hardware)s::text[]
                    OR ht.environment_misc->>'platform' = ANY(%(hardware)s::text[])
                  )
            )
            """
        )
        params["hardware"] = list(filters.filterHardware)

    post_join = ""
    if filters.filterBuildStatus:
        post_join = _post_join_status_clause(
            filters.filterBuildStatus,
            param_key="grouped_build_statuses",
            params=params,
        )

    return CompareFilterSql(
        pre_join="\n".join(pre_join),
        post_join=post_join,
        params=params,
    )


def build_boot_test_compare_filter_clauses(  # noqa: C901 - maps FilterParams fields to SQL AND clauses
    filters: Optional["FilterParams"],
    data_type: Literal["boots", "tests"],
) -> CompareFilterSql:
    """Build compare filters for boots/tests (identity pre-join, status post-join).

    Duration/issue filters are skipped on compare for the same reason as builds
    (ponytail: need paired-row columns before they can be filtered safely).
    """
    if filters is None:
        return CompareFilterSql()

    tab: Literal["boot", "test"] = "boot" if data_type == "boots" else "test"
    pre_join: list[str] = []
    params: dict = {}

    path_filter = (
        filters.filterBootPath if data_type == "boots" else filters.filterTestPath
    )
    if path_filter:
        pre_join.append("AND COALESCE(t.path, '') LIKE '%%' || %(test_path)s || '%%'")
        params["test_path"] = path_filter

    origin_filter = (
        filters.filter_boot_origin
        if data_type == "boots"
        else filters.filter_test_origin
    )
    if origin_filter:
        pre_join.append(
            "AND COALESCE(NULLIF(t.origin, ''), %(unknown_string)s)"
            " = ANY(%(test_origins)s)"
        )
        params["test_origins"] = list(origin_filter)
        params["unknown_string"] = UNKNOWN_STRING

    if filters.filterPlatforms[tab]:
        pre_join.append(
            "AND COALESCE(NULLIF(t.environment_misc->>'platform', ''),"
            " %(unknown_string)s) = ANY(%(platforms)s)"
        )
        params["platforms"] = list(filters.filterPlatforms[tab])
        params["unknown_string"] = UNKNOWN_STRING

    if filters.filterConfigs:
        pre_join.append(
            "AND COALESCE(NULLIF(b.config_name, ''), %(unknown_string)s)"
            " = ANY(%(configs)s)"
        )
        params["configs"] = list(filters.filterConfigs)
        params["unknown_string"] = UNKNOWN_STRING

    if filters.filterArchitecture:
        pre_join.append(
            "AND COALESCE(NULLIF(b.architecture, ''), %(unknown_string)s)"
            " = ANY(%(architectures)s)"
        )
        params["architectures"] = list(filters.filterArchitecture)
        params["unknown_string"] = UNKNOWN_STRING

    if filters.filterCompiler:
        pre_join.append(
            "AND COALESCE(NULLIF(b.compiler, ''), %(unknown_string)s)"
            " = ANY(%(compilers)s)"
        )
        params["compilers"] = list(filters.filterCompiler)
        params["unknown_string"] = UNKNOWN_STRING

    if filters.filter_labs:
        pre_join.append(
            "AND COALESCE(NULLIF(t.misc->>'runtime', ''), %(unknown_string)s)"
            " = ANY(%(labs)s)"
        )
        params["labs"] = list(filters.filter_labs)
        params["unknown_string"] = UNKNOWN_STRING

    if filters.filterHardware:
        pre_join.append(
            """
            AND (
                t.environment_compatible && %(hardware)s::text[]
                OR t.environment_misc->>'platform' = ANY(%(hardware)s::text[])
            )
            """
        )
        params["hardware"] = list(filters.filterHardware)

    status_filter = (
        filters.filterBootStatus if data_type == "boots" else filters.filterTestStatus
    )
    post_join = ""
    if status_filter:
        post_join = _post_join_status_clause(
            status_filter,
            param_key="grouped_test_statuses",
            params=params,
        )

    return CompareFilterSql(
        pre_join="\n".join(pre_join),
        post_join=post_join,
        params=params,
    )


@dataclass
class _HashAccumulator:
    builds: CompareStatusCounts = field(default_factory=CompareStatusCounts)
    boots: CompareStatusCounts = field(default_factory=CompareStatusCounts)
    tests: CompareStatusCounts = field(default_factory=CompareStatusCounts)


def _status_to_bucket(status: Optional[str]) -> BucketKey:
    if status is None:
        return "inconclusive"
    normalized = status.upper()
    if normalized == "PASS":
        return "pass"
    if normalized == "FAIL":
        return "fail"
    return "inconclusive"


def _increment_bucket(
    counts: CompareStatusCounts, bucket: BucketKey, amount: int
) -> None:
    if amount <= 0:
        return
    if bucket == "pass":
        counts.pass_count += amount
    elif bucket == "fail":
        counts.fail_count += amount
    else:
        counts.inconclusive += amount


def _rollup_status_to_bucket(status_name: str) -> BucketKey:
    if status_name == "PASS":
        return "pass"
    if status_name == "FAIL":
        return "fail"
    return "inconclusive"


def process_rollup_rows(
    *,
    rows: list[dict],
    commit_hashes: list[str],
) -> dict[str, _HashAccumulator]:
    accumulators = {commit_hash: _HashAccumulator() for commit_hash in commit_hashes}

    for row_dict in rows:
        commit_hash = row_dict["git_commit_hash"]
        is_boot_row = row_dict["is_boot"]
        acc = accumulators.setdefault(commit_hash, _HashAccumulator())
        target = acc.boots if is_boot_row else acc.tests

        for status_name, field_name in ROLLUP_STATUS_FIELDS.items():
            count = row_dict.get(field_name, 0) or 0
            if count <= 0:
                continue
            bucket = _rollup_status_to_bucket(status_name)
            _increment_bucket(target, bucket, count)

    return accumulators


def process_build_rows(
    *,
    rows: list[dict],
    commit_hashes: list[str],
) -> dict[str, _HashAccumulator]:
    accumulators = {commit_hash: _HashAccumulator() for commit_hash in commit_hashes}

    for row in rows:
        commit_hash = row["git_commit_hash"]
        count = row.get("count") or 0
        acc = accumulators.setdefault(commit_hash, _HashAccumulator())
        bucket = _status_to_bucket(row.get("status"))
        _increment_bucket(acc.builds, bucket, count)

    return accumulators


def _make_delta(
    side_a: CompareStatusCounts, side_b: CompareStatusCounts
) -> CompareDelta:
    return CompareDelta(
        **{
            "pass": side_b.pass_count - side_a.pass_count,
            "fail": side_b.fail_count - side_a.fail_count,
        }
    )


def change_counts_from_row(row: Optional[dict]) -> CompareChangeCounts:
    """Map a SQL aggregate row (snake_case keys) into CompareChangeCounts."""
    if not row:
        return CompareChangeCounts()
    return CompareChangeCounts(
        regression=row.get("regression") or 0,
        fixed=row.get("fixed") or 0,
        new_failure=row.get("new_failure") or 0,
        still_failing=row.get("still_failing") or 0,
        new_pass=row.get("new_pass") or 0,
        appeared=row.get("appeared") or 0,
        disappeared=row.get("disappeared") or 0,
    )


def _make_entity_summary(
    *,
    side_a: CompareStatusCounts,
    side_b: CompareStatusCounts,
    changes: Optional[CompareChangeCounts] = None,
) -> CompareEntitySummary:
    return CompareEntitySummary(
        sideA=side_a,
        sideB=side_b,
        delta=_make_delta(side_a, side_b),
        changes=changes or CompareChangeCounts(),
    )


def build_compare_response(
    *,
    hash_a: str,
    hash_b: str,
    tree_name: str,
    branch: str,
    git_url: str,
    accumulators: dict[str, _HashAccumulator],
    changes: Optional[dict[str, CompareChangeCounts]] = None,
) -> TreeCompareResponse:
    acc_a = accumulators.get(hash_a, _HashAccumulator())
    acc_b = accumulators.get(hash_b, _HashAccumulator())
    change_map = changes or {}

    return TreeCompareResponse(
        treeName=tree_name,
        branch=branch,
        gitUrl=git_url,
        summary=CompareSummary(
            builds=_make_entity_summary(
                side_a=acc_a.builds,
                side_b=acc_b.builds,
                changes=change_map.get("builds"),
            ),
            boots=_make_entity_summary(
                side_a=acc_a.boots,
                side_b=acc_b.boots,
                changes=change_map.get("boots"),
            ),
            tests=_make_entity_summary(
                side_a=acc_a.tests,
                side_b=acc_b.tests,
                changes=change_map.get("tests"),
            ),
        ),
    )
