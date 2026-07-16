from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Literal, Optional

from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.constants.process_pending import ROLLUP_STATUS_FIELDS
from kernelCI_app.typeModels.treeCompare import (
    CompareDelta,
    CompareEntitySummary,
    CompareGroupRow,
    CompareGroups,
    CompareStatusCounts,
    CompareSummary,
    TreeCompareResponse,
)

BucketKey = Literal["pass", "fail", "inconclusive"]


@dataclass
class _HashAccumulator:
    builds: CompareStatusCounts = field(default_factory=CompareStatusCounts)
    boots: CompareStatusCounts = field(default_factory=CompareStatusCounts)
    tests: CompareStatusCounts = field(default_factory=CompareStatusCounts)
    build_groups: dict[str, CompareStatusCounts] = field(
        default_factory=lambda: defaultdict(CompareStatusCounts)
    )
    boot_groups: dict[str, CompareStatusCounts] = field(
        default_factory=lambda: defaultdict(CompareStatusCounts)
    )
    test_groups: dict[str, CompareStatusCounts] = field(
        default_factory=lambda: defaultdict(CompareStatusCounts)
    )


def _empty_counts() -> CompareStatusCounts:
    return CompareStatusCounts()


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


def _boot_group_key(row_dict: dict) -> str:
    return (
        row_dict.get("test_platform")
        or row_dict.get("hardware_key")
        or UNKNOWN_STRING
    )


def _test_group_key(row_dict: dict) -> str:
    path_group = row_dict.get("path_group") or UNKNOWN_STRING
    arch = row_dict.get("build_architecture") or UNKNOWN_STRING
    if arch == UNKNOWN_STRING:
        return path_group
    return f"{path_group}/{arch}"


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
        group_id = _boot_group_key(row_dict) if is_boot_row else _test_group_key(row_dict)
        target = acc.boots if is_boot_row else acc.tests
        group_map = acc.boot_groups if is_boot_row else acc.test_groups

        for status_name, field_name in ROLLUP_STATUS_FIELDS.items():
            count = row_dict.get(field_name, 0) or 0
            if count <= 0:
                continue
            bucket = _rollup_status_to_bucket(status_name)
            _increment_bucket(target, bucket, count)
            _increment_bucket(group_map[group_id], bucket, count)

    return accumulators


def process_build_rows(
    *,
    rows: list[dict],
    commit_hashes: list[str],
) -> dict[str, _HashAccumulator]:
    accumulators = {commit_hash: _HashAccumulator() for commit_hash in commit_hashes}

    for row in rows:
        commit_hash = row["git_commit_hash"]
        config = row.get("config_name") or UNKNOWN_STRING
        count = row.get("count") or 0
        acc = accumulators.setdefault(commit_hash, _HashAccumulator())
        bucket = _status_to_bucket(row.get("status"))
        _increment_bucket(acc.builds, bucket, count)
        _increment_bucket(acc.build_groups[config], bucket, count)

    return accumulators


def _make_delta(side_a: CompareStatusCounts, side_b: CompareStatusCounts) -> CompareDelta:
    return CompareDelta(
        **{
            "pass": side_b.pass_count - side_a.pass_count,
            "fail": side_b.fail_count - side_a.fail_count,
        }
    )


def _make_entity_summary(
    *,
    side_a: CompareStatusCounts,
    side_b: CompareStatusCounts,
) -> CompareEntitySummary:
    return CompareEntitySummary(
        sideA=side_a,
        sideB=side_b,
        delta=_make_delta(side_a, side_b),
    )


def _make_group_rows(
    *,
    group_maps: tuple[dict[str, CompareStatusCounts], dict[str, CompareStatusCounts]],
    label_fn: Optional[Callable[[str], str]] = None,
) -> list[CompareGroupRow]:
    side_a_groups, side_b_groups = group_maps
    all_ids = set(side_a_groups) | set(side_b_groups)
    rows: list[CompareGroupRow] = []

    for group_id in all_ids:
        side_a = side_a_groups.get(group_id, _empty_counts())
        side_b = side_b_groups.get(group_id, _empty_counts())
        label = label_fn(group_id) if label_fn else group_id
        rows.append(
            CompareGroupRow(
                id=group_id,
                label=label,
                sideA=side_a,
                sideB=side_b,
                delta=_make_delta(side_a, side_b),
            )
        )

    return rows


def _test_group_label(group_id: str) -> str:
    if "/" in group_id:
        path_group, arch = group_id.split("/", 1)
        return f"{path_group} · {arch}"
    return group_id


def build_compare_response(
    *,
    hash_a: str,
    hash_b: str,
    tree_name: str,
    branch: str,
    git_url: str,
    accumulators: dict[str, _HashAccumulator],
) -> TreeCompareResponse:
    acc_a = accumulators.get(hash_a, _HashAccumulator())
    acc_b = accumulators.get(hash_b, _HashAccumulator())

    return TreeCompareResponse(
        treeName=tree_name,
        branch=branch,
        gitUrl=git_url,
        summary=CompareSummary(
            builds=_make_entity_summary(side_a=acc_a.builds, side_b=acc_b.builds),
            boots=_make_entity_summary(side_a=acc_a.boots, side_b=acc_b.boots),
            tests=_make_entity_summary(side_a=acc_a.tests, side_b=acc_b.tests),
        ),
        groups=CompareGroups(
            builds=_make_group_rows(
                group_maps=(acc_a.build_groups, acc_b.build_groups),
            ),
            boots=_make_group_rows(
                group_maps=(acc_a.boot_groups, acc_b.boot_groups),
            ),
            tests=_make_group_rows(
                group_maps=(acc_a.test_groups, acc_b.test_groups),
                label_fn=_test_group_label,
            ),
        ),
    )
