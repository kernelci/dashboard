from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional

from django.utils import timezone

from kernelCI_app.helpers.filters import (
    should_increment_build_issue,
    should_increment_test_issue,
)
from kernelCI_app.helpers.misc import handle_misc
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.issues import IssueDict
from kernelCI_app.typeModels.labDetails import (
    LabAttentionItem,
    LabAttentionResponse,
    LabBootRowItem,
    LabBootRowsResponse,
    LabBuildRowItem,
    LabBuildRowsResponse,
    LabDailyPoint,
    LabDetailsResponse,
    LabDetailsTreeItem,
    LabDistribution,
    LabFillStats,
    LabFrequencyCounts,
    LabTestRowItem,
    LabTestRowsResponse,
    LabTreeDailySeries,
)
from kernelCI_app.utils import (
    convert_issues_dict_to_list_typed,
    create_issue_typed,
    is_boot,
)


def parse_tree_filters(tree_params: list[str]) -> set[tuple[str, str]] | None:
    if not tree_params:
        return None
    parsed: set[tuple[str, str]] = set()
    for raw in tree_params:
        if "/" not in raw:
            continue
        tree_name, git_branch = raw.split("/", 1)
        if tree_name and git_branch:
            parsed.add((tree_name, git_branch))
    return parsed or None


def tree_key(tree_name: str, git_branch: str) -> str:
    return f"{tree_name}/{git_branch}"


def platform_from_row(row: dict) -> str:
    misc = handle_misc(row.get("test_environment_misc"))
    if not misc:
        return ""
    platform = misc.get("platform")
    return platform if isinstance(platform, str) else ""


def _day_range(interval_in_days: int) -> list[date]:
    today = timezone.localdate()
    start = today - timedelta(days=interval_in_days - 1)
    return [start + timedelta(days=offset) for offset in range(interval_in_days)]


def _increment_daily(
    daily: dict[date, dict[str, int]],
    *,
    when: Optional[datetime],
    status: Optional[str],
) -> None:
    if when is None:
        return
    day = when.date()
    if day not in daily:
        return
    bucket = "pass_count" if status == "PASS" else "fail_count"
    if status not in ("PASS", "FAIL"):
        bucket = "inconclusive_count"
    daily[day][bucket] += 1


def _new_daily_tracker(interval_in_days: int) -> dict[date, dict[str, int]]:
    return {
        day: {"pass_count": 0, "fail_count": 0, "inconclusive_count": 0}
        for day in _day_range(interval_in_days)
    }


def _daily_to_points(daily: dict[date, dict[str, int]]) -> list[LabDailyPoint]:
    return [
        LabDailyPoint(
            day=day,
            pass_count=values["pass_count"],
            fail_count=values["fail_count"],
            inconclusive_count=values["inconclusive_count"],
        )
        for day, values in sorted(daily.items())
    ]


@dataclass
class _TreeBucket:
    tree_name: str
    git_branch: str
    commit_name: Optional[str] = None
    commit_hash: Optional[str] = None
    commit_time: Optional[datetime] = None
    builds: StatusCount = field(default_factory=StatusCount)
    boots: StatusCount = field(default_factory=StatusCount)
    tests: StatusCount = field(default_factory=StatusCount)
    build_issues: IssueDict = field(default_factory=dict)
    boot_issues: IssueDict = field(default_factory=dict)
    test_issues: IssueDict = field(default_factory=dict)
    seen_builds: set[str] = field(default_factory=set)
    seen_tests: set[str] = field(default_factory=set)
    build_daily: dict[date, dict[str, int]] = field(default_factory=dict)
    boot_daily: dict[date, dict[str, int]] = field(default_factory=dict)
    test_daily: dict[date, dict[str, int]] = field(default_factory=dict)
    has_build: bool = False
    has_boot: bool = False
    has_test: bool = False


def _touch_commit(bucket: _TreeBucket, row: dict, when: Optional[datetime]) -> None:
    commit_hash = row.get("commit_hash")
    commit_name = row.get("commit_name")
    if not commit_hash or when is None:
        return
    if bucket.commit_time is None or when >= bucket.commit_time:
        bucket.commit_time = when
        bucket.commit_hash = commit_hash
        bucket.commit_name = commit_name


def _process_build_issue(bucket: _TreeBucket, row: dict) -> None:
    issue_id = row.get("issue_id")
    issue_version = row.get("issue_version")
    build_status = row.get("build_status")
    incident_test_id = row.get("incident_test_id")
    issue_id, issue_version, can_insert = should_increment_build_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
        build_status=build_status,
    )
    if not issue_id or issue_version is None or not can_insert:
        return
    key = (issue_id, issue_version)
    current = bucket.build_issues.get(key)
    if current:
        current.incidents_info.increment(build_status)
        return
    bucket.build_issues[key] = create_issue_typed(
        issue_id=issue_id,
        issue_version=issue_version,
        issue_comment=row.get("issue_comment"),
        issue_report_url=row.get("issue_report_url"),
        starting_count_status=build_status,
    )


def _process_test_issue(bucket: _TreeBucket, row: dict, *, boot: bool) -> None:
    issue_id = row.get("issue_id")
    issue_version = row.get("issue_version")
    test_status = row.get("test_status")
    incident_test_id = row.get("incident_test_id")
    issue_id, issue_version, can_insert = should_increment_test_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )
    if not issue_id or issue_version is None or not can_insert:
        return
    table = bucket.boot_issues if boot else bucket.test_issues
    key = (issue_id, issue_version)
    current = table.get(key)
    if current:
        current.incidents_info.increment(test_status)
        return
    table[key] = create_issue_typed(
        issue_id=issue_id,
        issue_version=issue_version,
        issue_comment=row.get("issue_comment"),
        issue_report_url=row.get("issue_report_url"),
        starting_count_status=test_status,
    )


def _frequency_list(counter: Counter[str]) -> list[LabFrequencyCounts]:
    return [
        LabFrequencyCounts(name=name, count=count)
        for name, count in counter.most_common()
        if name
    ]


def build_lab_details_response(  # noqa: C901 - one pass over build and test rows
    *,
    lab_name: str,
    interval_in_days: int,
    build_rows: list[dict],
    test_rows: list[dict],
) -> LabDetailsResponse:
    trees: dict[str, _TreeBucket] = {}
    platform_counter: Counter[str] = Counter()
    config_counter: Counter[str] = Counter()
    compiler_counter: Counter[str] = Counter()
    arch_counter: Counter[str] = Counter()
    lab_build_status = StatusCount()
    lab_boot_status = StatusCount()
    lab_test_status = StatusCount()
    builds_total = 0
    builds_with_duration = 0
    runs_total = 0
    runs_with_duration = 0
    runs_with_platform = 0
    runs_with_log_url = 0
    runs_with_log_excerpt = 0
    seen_build_ids: set[str] = set()
    seen_test_ids: set[str] = set()

    def bucket_for(row: dict) -> _TreeBucket:
        key = tree_key(row["tree_name"], row["git_branch"])
        if key not in trees:
            trees[key] = _TreeBucket(
                tree_name=row["tree_name"],
                git_branch=row["git_branch"],
                build_daily=_new_daily_tracker(interval_in_days),
                boot_daily=_new_daily_tracker(interval_in_days),
                test_daily=_new_daily_tracker(interval_in_days),
            )
        return trees[key]

    for row in build_rows:
        bucket = bucket_for(row)
        build_id = row["build_id"]
        when = row.get("build_start_time")
        _touch_commit(bucket, row, when)
        _process_build_issue(bucket, row)
        if build_id in bucket.seen_builds:
            continue
        bucket.seen_builds.add(build_id)
        bucket.has_build = True
        status = row.get("build_status")
        bucket.builds.increment(status)
        _increment_daily(bucket.build_daily, when=when, status=status)
        if build_id not in seen_build_ids:
            seen_build_ids.add(build_id)
            builds_total += 1
            lab_build_status.increment(status)
            if row.get("build_duration") is not None:
                builds_with_duration += 1

    for row in test_rows:
        bucket = bucket_for(row)
        test_id = row["test_id"]
        path = row.get("test_path")
        boot = is_boot(path)
        when = row.get("test_start_time")
        _touch_commit(bucket, row, when)
        _process_test_issue(bucket, row, boot=boot)
        if test_id in bucket.seen_tests:
            continue
        bucket.seen_tests.add(test_id)
        status = row.get("test_status")
        if boot:
            bucket.has_boot = True
            bucket.boots.increment(status)
            _increment_daily(bucket.boot_daily, when=when, status=status)
        else:
            bucket.has_test = True
            bucket.tests.increment(status)
            _increment_daily(bucket.test_daily, when=when, status=status)

        platform = platform_from_row(row)
        config_name = row.get("build_config_name") or ""
        arch = row.get("build_architecture") or ""
        compiler = row.get("build_compiler") or ""
        if test_id not in seen_test_ids:
            seen_test_ids.add(test_id)
            runs_total += 1
            if boot:
                lab_boot_status.increment(status)
            else:
                lab_test_status.increment(status)
            if row.get("test_duration") is not None:
                runs_with_duration += 1
            if platform and platform.strip():
                runs_with_platform += 1
            if row.get("test_log_url"):
                runs_with_log_url += 1
            if row.get("test_log_excerpt"):
                runs_with_log_excerpt += 1
            platform_counter[platform.strip()] += 1
            config_counter[config_name.strip()] += 1
            arch_counter[arch.strip()] += 1
            compiler_counter[compiler.strip()] += 1

    tree_items: list[LabDetailsTreeItem] = []
    for key, bucket in sorted(trees.items()):
        tree_items.append(
            LabDetailsTreeItem(
                key=key,
                tree_name=bucket.tree_name,
                git_branch=bucket.git_branch,
                commit_name=bucket.commit_name,
                commit_hash=bucket.commit_hash,
                builds=bucket.builds,
                boots=bucket.boots,
                tests=bucket.tests,
                build_issues=convert_issues_dict_to_list_typed(
                    issues_dict=bucket.build_issues
                ),
                boot_issues=convert_issues_dict_to_list_typed(
                    issues_dict=bucket.boot_issues
                ),
                test_issues=convert_issues_dict_to_list_typed(
                    issues_dict=bucket.test_issues
                ),
                daily=LabTreeDailySeries(
                    builds=_daily_to_points(bucket.build_daily),
                    boots=_daily_to_points(bucket.boot_daily),
                    tests=_daily_to_points(bucket.test_daily),
                ),
            )
        )

    checkout_total = len(trees)
    return LabDetailsResponse(
        lab_name=lab_name,
        trees=tree_items,
        distribution=LabDistribution(
            platforms=_frequency_list(platform_counter),
            configs=_frequency_list(config_counter),
            compilers=_frequency_list(compiler_counter),
            architectures=_frequency_list(arch_counter),
            build_status=lab_build_status,
            boot_status=lab_boot_status,
            test_status=lab_test_status,
        ),
        fill=LabFillStats(
            checkout_total=checkout_total,
            checkouts_built=sum(1 for bucket in trees.values() if bucket.has_build),
            checkouts_booted=sum(1 for bucket in trees.values() if bucket.has_boot),
            checkouts_tested=sum(1 for bucket in trees.values() if bucket.has_test),
            builds_total=builds_total,
            builds_with_duration=builds_with_duration,
            runs_total=runs_total,
            runs_with_duration=runs_with_duration,
            runs_with_platform=runs_with_platform,
            runs_with_log_url=runs_with_log_url,
            runs_with_log_excerpt=runs_with_log_excerpt,
        ),
    )


def build_lab_build_rows(build_rows: list[dict]) -> LabBuildRowsResponse:
    seen: set[str] = set()
    items: list[LabBuildRowItem] = []
    for row in build_rows:
        build_id = row["build_id"]
        if build_id in seen:
            continue
        seen.add(build_id)
        items.append(
            LabBuildRowItem(
                tree_name=row["tree_name"],
                git_branch=row["git_branch"],
                config_name=row.get("build_config_name") or "",
                architecture=row.get("build_architecture") or "",
                compiler=row.get("build_compiler") or "",
                status=row.get("build_status") or "",
                start_time=row.get("build_start_time"),
                duration=row.get("build_duration"),
            )
        )
    return LabBuildRowsResponse(builds=items)


def build_lab_boot_rows(test_rows: list[dict]) -> LabBootRowsResponse:
    seen: set[str] = set()
    items: list[LabBootRowItem] = []
    for row in test_rows:
        if not is_boot(row.get("test_path")):
            continue
        test_id = row["test_id"]
        if test_id in seen:
            continue
        seen.add(test_id)
        platform = platform_from_row(row)
        items.append(
            LabBootRowItem(
                tree_name=row["tree_name"],
                git_branch=row["git_branch"],
                platform=platform,
                config_name=row.get("build_config_name") or "",
                architecture=row.get("build_architecture") or "",
                compiler=row.get("build_compiler") or "",
                status=row.get("test_status") or "",
                start_time=row.get("test_start_time"),
                duration=row.get("test_duration"),
                log_url=row.get("test_log_url"),
                log_excerpt=row.get("test_log_excerpt"),
            )
        )
    return LabBootRowsResponse(boots=items)


def build_lab_test_rows(test_rows: list[dict], *, lab_name: str) -> LabTestRowsResponse:
    seen: set[str] = set()
    items: list[LabTestRowItem] = []
    for row in test_rows:
        if is_boot(row.get("test_path")):
            continue
        test_id = row["test_id"]
        if test_id in seen:
            continue
        seen.add(test_id)
        platform = platform_from_row(row)
        items.append(
            LabTestRowItem(
                id=test_id,
                status=row.get("test_status") or "",
                path=row.get("test_path"),
                start_time=row.get("test_start_time"),
                duration=row.get("test_duration"),
                tree_name=row["tree_name"],
                git_repository_branch=row["git_branch"],
                lab=lab_name,
                config_name=row.get("build_config_name"),
                architecture=row.get("build_architecture"),
                compiler=row.get("build_compiler"),
                platform=platform,
                log_url=row.get("test_log_url"),
                log_excerpt=row.get("test_log_excerpt"),
                environment_misc=row.get("test_environment_misc"),
            )
        )
    return LabTestRowsResponse(tests=items)


def build_lab_attention_response(rows: list[dict]) -> LabAttentionResponse:
    items: list[LabAttentionItem] = []
    for row in rows:
        kind = row["kind"]
        path = row["path"] if kind == "test" else "boot"
        items.append(
            LabAttentionItem(
                kind=kind,
                path=path,
                platform=row.get("platform") or "",
                tree_name=row["tree_name"],
                git_branch=row["git_branch"],
                commit_name=row.get("commit_name"),
                commit_hash=row.get("commit_hash"),
                config_name=row.get("config_name") or "",
                architecture=row.get("architecture") or "",
                compiler=row.get("compiler") or "",
                last_failure_date=row["last_failure_date"],
                passed_labs=sorted(row.get("passed_labs") or []),
            )
        )
    return LabAttentionResponse(items=items)
