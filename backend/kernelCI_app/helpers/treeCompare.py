from typing import Literal, Optional

from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.helpers.filters import FilterParams, is_filtered_out
from kernelCI_app.helpers.issueExtras import parse_issue
from kernelCI_app.typeModels.common import GroupedStatusLiteral
from kernelCI_app.typeModels.treeDetails import TreeCompareTest

CompareKey = tuple[str, str, str]
STATUS_RANK: dict[GroupedStatusLiteral, int] = {
    "PASS": 0,
    "INCONCLUSIVE": 1,
    "FAIL": 2,
}


def group_raw_status(status: Optional[str]) -> GroupedStatusLiteral:
    if status == "PASS":
        return "PASS"
    if status == "FAIL":
        return "FAIL"
    return "INCONCLUSIVE"


def worst_status(
    current: Optional[GroupedStatusLiteral],
    candidate: GroupedStatusLiteral,
) -> GroupedStatusLiteral:
    if current is None:
        return candidate
    if STATUS_RANK[candidate] > STATUS_RANK[current]:
        return candidate
    return current


def is_compare_row_filtered_out(
    *,
    filters: FilterParams,
    data_type: Literal["boots", "tests"],
    path: str,
    status: Optional[str],
    config: str,
    lab: str,
    compiler: str,
    architecture: str,
    platform: str,
    origin: Optional[str],
    compatibles: set[str],
    known_issues: set[tuple[str, Optional[int]]],
) -> bool:
    tab: Literal["boot", "test"] = "boot" if data_type == "boots" else "test"
    status_filter = (
        filters.filterBootStatus if data_type == "boots" else filters.filterTestStatus
    )
    path_filter = (
        filters.filterBootPath if data_type == "boots" else filters.filterTestPath
    )
    origin_filter = (
        filters.filter_boot_origin
        if data_type == "boots"
        else filters.filter_test_origin
    )
    issue_filter = filters.filterIssues[tab]

    return bool(
        is_filtered_out(status or "NULL", status_filter)
        or (path_filter and path_filter not in path)
        or is_filtered_out(platform, filters.filterPlatforms[tab])
        or is_filtered_out(origin or UNKNOWN_STRING, origin_filter)
        or is_filtered_out(compiler, filters.filterCompiler)
        or is_filtered_out(config, filters.filterConfigs)
        or is_filtered_out(lab, filters.filter_labs)
        or is_filtered_out(architecture, filters.filterArchitecture)
        or (filters.filterHardware and filters.filterHardware.isdisjoint(compatibles))
        or (issue_filter and not known_issues.issubset(issue_filter))
    )


def collapse_side_statuses(
    *,
    rows: list[dict],
    commit_a: str,
    commit_b: str,
    filters: FilterParams,
    data_type: Literal["boots", "tests"],
) -> tuple[
    dict[CompareKey, GroupedStatusLiteral], dict[CompareKey, GroupedStatusLiteral]
]:
    """Filter rows once and collapse each commit to worst status per identity key.

    Duration filters are applied in SQL. Issue matching follows the
    hardwareDetailsSummary subset pattern on aggregated known_issues.
    """
    sides: dict[str, dict[CompareKey, GroupedStatusLiteral]] = {
        commit_a: {},
        commit_b: {},
    }

    for instance in rows:
        side = sides.get(instance["git_commit_hash"])
        if side is None:
            continue

        path = instance["path"] or UNKNOWN_STRING
        config = instance["config_name"] or UNKNOWN_STRING
        platform = instance["platform"] or UNKNOWN_STRING
        lab = instance["lab"] or UNKNOWN_STRING
        status = instance["status"]
        compatibles = set(instance["environment_compatible"] or [])
        (compiler, architecture) = [
            (val or UNKNOWN_STRING).strip(" []'")
            for val in (instance["compiler_arch"] or [None, None])
        ]
        known_issues = {
            parse_issue(issue) for issue in (instance["known_issues"] or [])
        }

        if is_compare_row_filtered_out(
            filters=filters,
            data_type=data_type,
            path=path,
            status=status,
            config=config,
            lab=lab,
            compiler=compiler,
            architecture=architecture,
            platform=platform,
            origin=instance["origin"],
            compatibles=compatibles,
            known_issues=known_issues,
        ):
            continue

        key: CompareKey = (path, config, platform)
        side[key] = worst_status(side.get(key), group_raw_status(status))

    return sides[commit_a], sides[commit_b]


def build_compare_rows(
    status_a: dict[CompareKey, GroupedStatusLiteral],
    status_b: dict[CompareKey, GroupedStatusLiteral],
    *,
    full: bool = False,
) -> list[TreeCompareTest]:
    """Return differing rows, or every row when full is enabled."""
    keys = set(status_a) | set(status_b)
    rows: list[TreeCompareTest] = []

    for path, config_name, platform in sorted(keys):
        a = status_a.get((path, config_name, platform))
        b = status_b.get((path, config_name, platform))
        if not full and a == b:
            continue
        rows.append(
            TreeCompareTest(
                path=path,
                config_name=config_name,
                platform=platform,
                status_a=a,
                status_b=b,
            )
        )

    return rows
