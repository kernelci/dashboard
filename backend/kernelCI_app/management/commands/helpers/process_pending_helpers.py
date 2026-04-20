import hashlib
from typing import NamedTuple, Optional, Sequence, TypedDict

from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.constants.process_pending import ROLLUP_STATUS_FIELDS
from kernelCI_app.helpers.logger import logger
from kernelCI_app.models import Builds, Checkouts, Incidents, PendingTest, StatusChoices


def get_rollup_key(test_id: str) -> bytes:
    """Generate a hash (rollup key) from test_id with 'rollup|' prefix for namespacing."""
    return hashlib.sha256(f"rollup|{test_id}".encode("utf-8")).digest()


EMPTY_PATH_GROUP = "-"


class RollupKey(NamedTuple):
    origin: str
    tree_name: str
    git_repository_branch: str
    git_repository_url: str
    git_commit_hash: str
    path_group: str
    config: str
    arch: str
    compiler: str
    hardware_key: str
    platform: Optional[str]
    lab: Optional[str]
    test_origin: str
    issue_id: Optional[str]
    issue_version: Optional[int]
    issue_uncategorized: bool
    is_boot: bool


class RollupEntryData(TypedDict):
    checkout: Checkouts
    path_group: str
    config: str
    arch: str
    compiler: str
    hardware_key: str
    platform: Optional[str]
    lab: Optional[str]
    origin: str
    issue_id: Optional[str]
    issue_version: Optional[int]
    issue_uncategorized: bool
    is_boot: bool
    status: StatusChoices


def extract_path_group(path: str) -> str:
    """Extract the path group from a path."""
    return path.split(".", 1)[0] if path else EMPTY_PATH_GROUP


def accumulate_rollup_entry(
    rollup_data: dict[tuple, dict],
    entry: RollupEntryData,
    *,
    is_correction: bool = False,
) -> None:
    """Accumulate a single test entry into rollup_data in-place."""
    checkout = entry["checkout"]
    rollup_key = RollupKey(
        origin=checkout.origin,
        tree_name=checkout.tree_name,
        git_repository_branch=checkout.git_repository_branch,
        git_repository_url=checkout.git_repository_url,
        git_commit_hash=checkout.git_commit_hash,
        path_group=entry["path_group"],
        config=entry["config"],
        arch=entry["arch"],
        compiler=entry["compiler"],
        hardware_key=entry["hardware_key"],
        platform=entry["platform"],
        lab=entry["lab"],
        test_origin=entry["origin"],
        issue_id=entry["issue_id"],
        issue_version=entry["issue_version"],
        issue_uncategorized=entry["issue_uncategorized"],
        is_boot=entry["is_boot"],
    )

    record = rollup_data.setdefault(
        rollup_key,
        {
            "pass_tests": 0,
            "fail_tests": 0,
            "skip_tests": 0,
            "error_tests": 0,
            "miss_tests": 0,
            "done_tests": 0,
            "null_tests": 0,
            "total_tests": 0,
        },
    )

    counter = ROLLUP_STATUS_FIELDS.get(entry["status"], "null_tests")

    if is_correction:
        record["null_tests"] -= 1
        record[counter] += 1
    else:
        record[counter] += 1
        record["total_tests"] += 1


def aggregate_tests_rollup(
    ready_tests: Sequence[PendingTest],
    test_builds_by_id: dict[str, Builds],
    issues_map: dict[str, dict],
    reprocess_test_ids: set[str] | None = None,
) -> dict[tuple, dict]:
    """
    Build rollup data from pending tests.
    Returns rollup data without touching the database.
    """
    rollup_data: dict[tuple, dict] = {}

    if reprocess_test_ids is None:
        reprocess_test_ids = set()

    for test in ready_tests:
        # shouldn't happen, but being defensive here
        try:
            build = test_builds_by_id[test.build_id]
        except KeyError:
            logger.warning(
                f"Found test {test.test_id} with no build {test.build_id} on aggregate_tests_rollup"
            )
            continue

        checkout = build.checkout
        path = test.path or ""
        path_group = extract_path_group(path)

        hardware_key = UNKNOWN_STRING
        if test.compatible:
            hardware_key = test.compatible[0]
        elif test.platform:
            hardware_key = test.platform

        issue_info = issues_map.get(test.test_id, {})
        issue_id = issue_info.get("issue_id")
        issue_version = issue_info.get("issue_version")
        issue_uncategorized = (
            issue_id is None and test.full_status == StatusChoices.FAIL
        )

        arch = build.architecture or UNKNOWN_STRING
        compiler = build.compiler or UNKNOWN_STRING
        config = build.config_name or UNKNOWN_STRING

        accumulate_rollup_entry(
            rollup_data,
            {
                "checkout": checkout,
                "path_group": path_group,
                "config": config,
                "arch": arch,
                "compiler": compiler,
                "hardware_key": hardware_key,
                "platform": test.platform,
                "lab": test.lab,
                "origin": test.origin,
                "issue_id": issue_id,
                "issue_version": issue_version,
                "issue_uncategorized": issue_uncategorized,
                "is_boot": test.is_boot,
                "status": test.full_status,
            },
            is_correction=test.test_id in reprocess_test_ids,
        )

    return rollup_data


def fetch_test_issues(test_ids: list[str]) -> dict[str, dict]:
    """
    Bulk-fetch the first (earliest) incident per test_id.

    Returns a mapping {test_id: {"issue_id": ..., "issue_version": ...}}.
    "First" is defined as the earliest incident ordered by test_id,
    field_timestamp, and id to ensure deterministic results.
    """
    issues_map: dict[str, dict] = {}
    incidents = (
        Incidents.objects.filter(test_id__in=test_ids)
        .order_by("test_id", "field_timestamp", "id")
        .values("test_id", "issue_id", "issue_version")
    )

    for inc in incidents:
        issues_map.setdefault(
            inc["test_id"],
            {
                "issue_id": inc["issue_id"],
                "issue_version": inc["issue_version"],
            },
        )

    return issues_map
