from collections import defaultdict
from kernelCI_app.typeModels.hardwareDetails import Tree
from kernelCI_app.typeModels.commonDetails import (
    TestArchSummaryItem,
    BuildSummary,
    TestSummary,
    BuildArchitectures,
)
from kernelCI_app.typeModels.common import StatusCount


def create_tree(**overrides):
    """Create Tree."""
    base_tree = Tree(
        index="1",
        origin="test",
        tree_name="mainline",
        git_repository_branch="master",
        git_repository_url="https://git.kernel.org",
        head_git_commit_name="commit1",
        head_git_commit_hash="abc123",
        head_git_commit_tag=["v5.4"],
        selected_commit_status=None,
        is_selected=True,
    )

    for key, value in overrides.items():
        setattr(base_tree, key, value)

    return base_tree


def create_tree_status_summary(**overrides):
    """Create tree status summary."""
    summary = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    summary["1"]["builds"]["PASS"] = 5
    summary["2"]["builds"]["FAIL"] = 2

    for tree_id, tree_data in overrides.items():
        for category, status_data in tree_data.items():
            for status, count in status_data.items():
                summary[tree_id][category][status] = count

    return summary


def create_test_record(**overrides):
    """Create test record."""
    base_record = {
        "path": "test.specific",
        "status": "PASS",
        "build_id": "build123",
        "test_id": "test123",
        "duration": 100,
        "start_time": "2024-01-15T10:00:00Z",
        "environment_compatible": ["hardware1"],
        "environment_misc": {"platform": "x86_64"},
        "origin": "test",
        "incident_id": "incident123",
        "incident_test_id": "test123",
        "incident_is_culprit": True,
        "issue_id": "issue123",
        "issue_version": 1,
        "issue_comment": "Test issue",
        "issue_report_url": "http://example.com",
    }

    base_record.update(overrides)
    return base_record


def create_build_record(**overrides):
    """Create build record."""
    base_record = {
        "build_id": "build123",
        "status": "PASS",
        "duration": 200,
        "start_time": "2024-01-15T09:00:00Z",
        "architecture": "x86_64",
        "compiler": "gcc",
        "config_name": "defconfig",
        "config_url": "http://config.com",
        "log_url": "http://log.com",
        "origin": "test",
        "command": "make",
        "comment": "Test build",
        "tree_name": "mainline",
        "git_commit_hash": "abc123",
        "git_commit_name": "commit1",
        "git_commit_tag": ["v5.4"],
        "git_repository_url": "https://git.kernel.org",
        "git_repository_branch": "master",
    }

    base_record.update(overrides)
    return base_record


def create_issue_record(**overrides):
    """Create issue record."""
    base_record = {
        "issue_id": "issue123",
        "issue_version": 1,
        "issue_comment": "Test issue",
        "issue_report_url": "http://example.com",
        "incidents_info": StatusCount(
            DONE=0, PASS=1, FAIL=0, ERROR=0, SKIP=0, MISS=0, NULL=0
        ),
    }

    base_record.update(overrides)
    return base_record


def create_test_arch_summary_item(**overrides):
    """Create TestArchSummaryItem."""
    base_item = TestArchSummaryItem(
        arch="x86_64",
        compiler="gcc",
        status=StatusCount(DONE=0, PASS=5, FAIL=2, ERROR=1, SKIP=0, MISS=0, NULL=0),
    )

    for key, value in overrides.items():
        setattr(base_item, key, value)

    return base_item


def create_build_summary(**overrides):
    """Create BuildSummary."""
    base_summary = BuildSummary(
        status=StatusCount(DONE=0, PASS=10, FAIL=3, ERROR=1, SKIP=0, MISS=0, NULL=0),
        architectures={
            "x86_64": BuildArchitectures(
                DONE=0, PASS=5, FAIL=2, ERROR=1, SKIP=0, MISS=0, NULL=0
            ),
            "arm64": BuildArchitectures(
                DONE=0, PASS=5, FAIL=1, ERROR=0, SKIP=0, MISS=0, NULL=0
            ),
        },
        configs={
            "defconfig": StatusCount(
                DONE=0, PASS=8, FAIL=2, ERROR=1, SKIP=0, MISS=0, NULL=0
            ),
            "allmodconfig": StatusCount(
                DONE=0, PASS=2, FAIL=1, ERROR=0, SKIP=0, MISS=0, NULL=0
            ),
        },
        issues=[],
        unknown_issues=0,
    )

    for key, value in overrides.items():
        setattr(base_summary, key, value)

    return base_summary


def create_test_summary(**overrides):
    """Create TestSummary."""
    base_summary = TestSummary(
        status=StatusCount(DONE=0, PASS=50, FAIL=10, ERROR=2, SKIP=5, MISS=1, NULL=0),
        origins={
            "test": StatusCount(
                DONE=0, PASS=30, FAIL=5, ERROR=1, SKIP=3, MISS=0, NULL=0
            ),
            "boot": StatusCount(
                DONE=0, PASS=20, FAIL=5, ERROR=1, SKIP=2, MISS=1, NULL=0
            ),
        },
        architectures=[
            TestArchSummaryItem(
                arch="x86_64",
                compiler="gcc",
                status=StatusCount(
                    DONE=0, PASS=25, FAIL=5, ERROR=1, SKIP=2, MISS=0, NULL=0
                ),
            ),
            TestArchSummaryItem(
                arch="arm64",
                compiler="gcc",
                status=StatusCount(
                    DONE=0, PASS=25, FAIL=5, ERROR=1, SKIP=3, MISS=1, NULL=0
                ),
            ),
        ],
        configs={
            "defconfig": StatusCount(
                DONE=0, PASS=40, FAIL=8, ERROR=1, SKIP=4, MISS=0, NULL=0
            ),
            "allmodconfig": StatusCount(
                DONE=0, PASS=10, FAIL=2, ERROR=1, SKIP=1, MISS=1, NULL=0
            ),
        },
        issues=[],
        unknown_issues=0,
        fail_reasons=defaultdict(
            int, {"Test failure": 5, "Timeout": 3, "Memory error": 2}
        ),
        failed_platforms={"x86_64", "arm64"},
        environment_compatible={"hardware1": StatusCount()},
        environment_misc={"x86_64": StatusCount()},
    )

    for key, value in overrides.items():
        setattr(base_summary, key, value)

    return base_summary


base_tree = create_tree()

tree_with_selected_commit = create_tree(selected_commit_status={"builds": {"PASS": 5}})

tree_with_different_commit = create_tree(
    index="2",
    tree_name="stable",
    git_repository_branch="linux-5.4.y",
    head_git_commit_name="commit2",
    head_git_commit_hash="def456",
    head_git_commit_tag=["v5.4.1"],
)

base_tree_status_summary = create_tree_status_summary()

base_test_record = create_test_record()

test_record_with_fail = create_test_record(
    status="FAIL",
    path="boot.test",
)

base_build_record = create_build_record()

build_record_with_fail = create_build_record(
    status="FAIL",
    architecture="arm64",
)

base_issue_record = create_issue_record()

base_test_arch_summary_item = create_test_arch_summary_item()

base_build_summary = create_build_summary()

base_test_summary = create_test_summary()


def create_process_filters_instance(**overrides):
    """Create instance for process_filters tests."""
    from unittest.mock import MagicMock

    instance = MagicMock()
    instance.global_configs = set()
    instance.global_architectures = set()
    instance.global_compilers = set()
    instance.unfiltered_build_issues = set()
    instance.unfiltered_boot_issues = set()
    instance.unfiltered_test_issues = set()
    instance.unfiltered_boot_platforms = set()
    instance.unfiltered_test_platforms = set()
    instance.unfiltered_uncategorized_issue_flags = {}
    instance.unfiltered_origins = {"build": set(), "boot": set(), "test": set()}

    for key, value in overrides.items():
        setattr(instance, key, value)

    return instance


def create_process_filters_record(**overrides):
    """Create record for process_filters tests."""
    base_record = {
        "id": "test123",
        "path": "test.specific",
        "status": "PASS",
        "environment_misc": "{}",
        "test_origin": "test",
        "build_id": "build123",
        "incidents__test_id": "test123",
        "incidents__issue__id": "test_issue123",
        "incidents__issue__version": 2,
        "build__incidents__issue__id": "issue123",
        "build__incidents__issue__version": 1,
        "build__status": "PASS",
        "build__config_name": "defconfig",
        "build__architecture": "x86_64",
        "build__compiler": "gcc",
        "build__origin": "test",
    }

    base_record.update(overrides)
    return base_record


def create_handle_test_summary_record(**overrides):
    """Create record for handle_test_summary tests."""
    base_record = {
        "status": "PASS",
        "build__config_name": "defconfig",
        "build__architecture": "x86_64",
        "build__compiler": "gcc",
        "environment_misc": "{}",
        "misc": "{}",
        "test_origin": "test",
    }

    base_record.update(overrides)
    return base_record


process_filters_instance = create_process_filters_instance()

process_filters_instance_without_build = create_process_filters_instance()

process_filters_record_with_build = create_process_filters_record()

process_filters_record_without_build = create_process_filters_record(
    id=None,
    build_id=None,
)

process_filters_record_boot = create_process_filters_record(
    id="boot123",
    path="boot.test",
    test_origin="boot",
    build_id=None,
    incidents__issue__id="boot_issue123",
    incidents__issue__version=1,
)

handle_test_summary_record_basic = create_handle_test_summary_record()

handle_test_summary_record_new_config = create_handle_test_summary_record(
    build__config_name="newconfig",
)

handle_test_summary_record_new_platform = create_handle_test_summary_record(
    status="FAIL",
    environment_misc='{"platform": "newplatform"}',
    misc='{"error_msg": "Test failed"}',
)

handle_test_summary_record_new_origin = create_handle_test_summary_record(
    test_origin="neworigin",
)
