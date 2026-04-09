from collections import defaultdict
from unittest.mock import MagicMock, patch

from kernelCI_app.constants.general import UNCATEGORIZED_STRING, UNKNOWN_STRING
from kernelCI_app.helpers.hardwareDetails import generate_test_summary_typed
from kernelCI_app.helpers.treeDetailsRollup import (
    ROLLUP_TEST_ID,
    normalize_build_dict,
    process_build_filters,
    process_rollup_filters,
    process_rollup_issues,
    process_rollup_summary,
    rollup_test_or_boot_filtered_out,
)
from kernelCI_app.typeModels.databases import FAIL_STATUS, NULL_STATUS


def _base_rollup_row(**overrides):
    row = {
        "build_config_name": "defconfig",
        "build_architecture": "arm64",
        "build_compiler": "gcc",
        "hardware_key": "hw-1",
        "test_platform": "qemu",
        "test_origin": "origin-a",
        "test_lab": "lab-1",
        "path_group": "group.a",
        "issue_id": None,
        "issue_version": None,
        "issue_uncategorized": False,
        "pass_tests": 0,
        "fail_tests": 0,
        "skip_tests": 0,
        "error_tests": 0,
        "miss_tests": 0,
        "done_tests": 0,
        "null_tests": 0,
    }
    row.update(overrides)
    return row


class FakeRollupTreeInstance:
    """Minimal stand-in for tree details views used by rollup helpers."""

    def __init__(self):
        self.filters = MagicMock()
        self.filters.filterBootPath = ""
        self.filters.filterTestPath = ""
        self.filters.filterIssues = {"boot": set(), "test": set()}
        self.filters.filterPlatforms = {"boot": set(), "test": set()}
        self.filters.filter_boot_origin = set()
        self.filters.filter_test_origin = set()
        self.filters.filterBootStatus = []
        self.filters.filterTestStatus = []

        self.bootStatusSummary = {}
        self.testStatusSummary = {}
        self.bootArchSummary = {}
        self.test_arch_summary = {}
        self.bootConfigs = {}
        self.test_configs = {}
        self.bootPlatformsFailing = set()
        self.testPlatformsWithErrors = set()
        self.bootEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.testEnvironmentCompatible = defaultdict(lambda: defaultdict(int))
        self.bootEnvironmentMisc = defaultdict(lambda: defaultdict(int))
        self.testEnvironmentMisc = defaultdict(lambda: defaultdict(int))
        self.boot_summary = {"origins": {}}
        self.test_summary = {"origins": {}}
        self.boot_summary_typed = generate_test_summary_typed()
        self.test_summary_typed = generate_test_summary_typed()

        self.global_configs = set()
        self.global_architectures = set()
        self.global_compilers = set()
        self.unfiltered_origins = {"build": set(), "boot": set(), "test": set()}
        self.unfiltered_labs = {"build": set(), "boot": set(), "test": set()}
        self.unfiltered_build_issues = set()
        self.unfiltered_boot_issues = set()
        self.unfiltered_test_issues = set()
        self.unfiltered_uncategorized_issue_flags = {
            "build": False,
            "boot": False,
            "test": False,
        }

        self.boot_issues_dict = {}
        self.test_issues_dict = {}
        self.failed_boots_with_unknown_issues = 0
        self.failed_tests_with_unknown_issues = 0


class TestNormalizeBuildDict:
    @patch("kernelCI_app.helpers.treeDetailsRollup.is_status_failure")
    @patch("kernelCI_app.helpers.treeDetailsRollup.handle_misc")
    def test_sets_defaults_and_normalizes_misc(
        self, mock_handle_misc, mock_is_status_failure
    ):
        mock_handle_misc.return_value = {"lab": "lab-x"}
        mock_is_status_failure.return_value = False

        row = {"build_misc": None}
        normalize_build_dict(row)

        assert row["build_misc"] == {"lab": "lab-x"}
        assert row["build_status"] == NULL_STATUS
        assert row["build_architecture"] == UNKNOWN_STRING
        assert row["build_compiler"] == UNKNOWN_STRING
        assert row["build_config_name"] == UNKNOWN_STRING
        mock_handle_misc.assert_called_once_with(None)

    @patch("kernelCI_app.helpers.treeDetailsRollup.is_status_failure")
    @patch("kernelCI_app.helpers.treeDetailsRollup.handle_misc")
    def test_sets_uncategorized_issue_on_failed_build_without_issue_id(
        self, mock_handle_misc, mock_is_status_failure
    ):
        mock_handle_misc.return_value = None
        mock_is_status_failure.return_value = True

        row = {"build_status": FAIL_STATUS, "issue_id": None}
        normalize_build_dict(row)

        assert row["issue_id"] == UNCATEGORIZED_STRING

    @patch("kernelCI_app.helpers.treeDetailsRollup.is_status_failure")
    @patch("kernelCI_app.helpers.treeDetailsRollup.handle_misc")
    def test_preserves_existing_issue_id_on_failure(
        self, mock_handle_misc, mock_is_status_failure
    ):
        mock_handle_misc.return_value = None
        mock_is_status_failure.return_value = True

        row = {"build_status": FAIL_STATUS, "issue_id": "known"}
        normalize_build_dict(row)

        assert row["issue_id"] == "known"


class TestProcessBuildFilters:
    def test_populates_globals_and_build_issue_for_failed_build(self):
        inst = FakeRollupTreeInstance()
        row = {
            "build_status": FAIL_STATUS,
            "build_config_name": "c1",
            "build_architecture": "x86",
            "build_compiler": "clang",
            "build_origin": "maestro",
            "build_misc": {"lab": "l1"},
            "issue_id": "issue123",
            "issue_version": 2,
            "incident_test_id": None,
        }
        process_build_filters(inst, row)

        assert inst.global_configs == {"c1"}
        assert inst.global_architectures == {"x86"}
        assert inst.global_compilers == {"clang"}
        assert inst.unfiltered_origins["build"] == {"maestro"}
        assert inst.unfiltered_labs["build"] == {"l1"}
        assert ("issue123", 2) in inst.unfiltered_build_issues

    def test_skips_build_issue_increment_for_test_only_incident(self):
        inst = FakeRollupTreeInstance()
        row = {
            "build_status": FAIL_STATUS,
            "build_config_name": "c1",
            "build_architecture": "x86",
            "build_compiler": "clang",
            "build_origin": "maestro",
            "build_misc": None,
            "issue_id": "issue456",
            "issue_version": 2,
            "incident_test_id": "some-test",
        }
        process_build_filters(inst, row)

        assert inst.unfiltered_build_issues == set()
        assert inst.unfiltered_labs["build"] == set()


class TestProcessRollupFilters:
    def test_boot_row_updates_boot_sets(self):
        inst = FakeRollupTreeInstance()
        row = {
            "is_boot": True,
            "issue_id": "issue123",
            "issue_version": 1,
            "issue_uncategorized": False,
            "test_origin": "origin1",
            "test_lab": "lab1",
        }
        process_rollup_filters(inst, row)

        assert inst.unfiltered_origins["boot"] == {"origin1"}
        assert inst.unfiltered_labs["boot"] == {"lab1"}
        assert ("issue123", 1) in inst.unfiltered_boot_issues

    def test_test_row_updates_test_sets(self):
        inst = FakeRollupTreeInstance()
        row = {
            "is_boot": False,
            "issue_id": None,
            "issue_version": None,
            "issue_uncategorized": True,
        }
        process_rollup_filters(inst, row)

        assert inst.unfiltered_origins["test"] == {UNKNOWN_STRING}
        assert inst.unfiltered_labs["test"] == {UNKNOWN_STRING}
        assert inst.unfiltered_uncategorized_issue_flags["test"] is True

    def test_none_origin_and_lab_are_normalized_to_unknown(self):
        inst = FakeRollupTreeInstance()
        row = {
            "is_boot": False,
            "issue_id": None,
            "issue_version": None,
            "issue_uncategorized": False,
            "test_origin": None,
            "test_lab": None,
        }
        process_rollup_filters(inst, row)

        assert inst.unfiltered_origins["test"] == {UNKNOWN_STRING}
        assert inst.unfiltered_labs["test"] == {UNKNOWN_STRING}


class TestRollupTestOrBootFilteredOut:
    def test_filtered_by_path(self):
        inst = FakeRollupTreeInstance()
        inst.filters.filterTestPath = "wanted"
        row = _base_rollup_row(path_group="other")

        assert (
            rollup_test_or_boot_filtered_out(inst, row_dict=row, is_boot_row=False)
            is True
        )

    def test_not_filtered_when_filter_path_empty(self):
        inst = FakeRollupTreeInstance()
        inst.filters.filterTestPath = ""
        row = _base_rollup_row()

        assert (
            rollup_test_or_boot_filtered_out(inst, row_dict=row, is_boot_row=False)
            is False
        )

    @patch("kernelCI_app.helpers.treeDetailsRollup.should_filter_test_issue")
    def test_delegates_to_issue_filter(self, mock_should_filter):
        mock_should_filter.return_value = True
        inst = FakeRollupTreeInstance()
        row = _base_rollup_row(issue_id="i1", issue_version=1)

        assert (
            rollup_test_or_boot_filtered_out(inst, row_dict=row, is_boot_row=False)
            is True
        )
        mock_should_filter.assert_called_once()
        call_kw = mock_should_filter.call_args.kwargs
        assert call_kw["incident_test_id"] == ROLLUP_TEST_ID

    def test_filtered_by_platform(self):
        inst = FakeRollupTreeInstance()
        inst.filters.filterPlatforms["test"] = {"p1"}
        row = _base_rollup_row(test_platform="p2")

        assert (
            rollup_test_or_boot_filtered_out(inst, row_dict=row, is_boot_row=False)
            is True
        )

    def test_filtered_by_origin(self):
        inst = FakeRollupTreeInstance()
        inst.filters.filter_test_origin = {"allowed"}
        row = _base_rollup_row(test_origin="other")

        assert (
            rollup_test_or_boot_filtered_out(inst, row_dict=row, is_boot_row=False)
            is True
        )

    @patch("kernelCI_app.helpers.treeDetailsRollup.should_filter_test_issue")
    def test_uncategorized_sets_issue_id_for_filtering(self, mock_should_filter):
        mock_should_filter.return_value = False
        inst = FakeRollupTreeInstance()
        inst.filters.filterIssues["test"] = {UNCATEGORIZED_STRING}
        row = _base_rollup_row(issue_uncategorized=True)

        assert (
            rollup_test_or_boot_filtered_out(inst, row_dict=row, is_boot_row=False)
            is False
        )
        call_kw = mock_should_filter.call_args.kwargs
        assert call_kw["issue_id"] == UNCATEGORIZED_STRING

    def test_boot_filtered_by_boot_path(self):
        inst = FakeRollupTreeInstance()
        inst.filters.filterBootPath = "wanted"
        row = _base_rollup_row(path_group="other")

        assert (
            rollup_test_or_boot_filtered_out(inst, row_dict=row, is_boot_row=True)
            is True
        )

    def test_boot_not_filtered_by_test_path_when_is_boot_row(self):
        inst = FakeRollupTreeInstance()
        inst.filters.filterTestPath = "wanted"
        inst.filters.filterBootPath = ""
        row = _base_rollup_row(path_group="other")

        assert (
            rollup_test_or_boot_filtered_out(inst, row_dict=row, is_boot_row=True)
            is False
        )


class TestProcessRollupSummary:
    def test_accumulates_test_counts_without_status_filter(self):
        inst = FakeRollupTreeInstance()
        row = _base_rollup_row(pass_tests=2, fail_tests=1)

        process_rollup_summary(inst, row_dict=row, is_boot_row=False)

        assert inst.testStatusSummary["PASS"] == 2
        assert inst.testStatusSummary["FAIL"] == 1
        assert inst.testPlatformsWithErrors == {"qemu"}
        arch_key = ("arm64", "gcc")
        assert inst.test_arch_summary[arch_key]["status"]["PASS"] == 2
        assert inst.test_arch_summary[arch_key]["status"]["FAIL"] == 1
        assert inst.test_configs["defconfig"]["PASS"] == 2
        assert inst.test_configs["defconfig"]["FAIL"] == 1

    def test_skips_row_when_status_filter_has_no_overlap(self):
        inst = FakeRollupTreeInstance()
        inst.filters.filterTestStatus = ["SKIP"]
        row = _base_rollup_row(pass_tests=5)

        process_rollup_summary(inst, row_dict=row, is_boot_row=False)

        assert inst.testStatusSummary == {}

    def test_applies_partial_status_filter_to_counts(self):
        inst = FakeRollupTreeInstance()
        inst.filters.filterTestStatus = ["PASS"]
        row = _base_rollup_row(pass_tests=3, fail_tests=2)

        process_rollup_summary(inst, row_dict=row, is_boot_row=False)

        assert inst.testStatusSummary == {"PASS": 3}

    def test_routes_compatible_vs_misc_environment(self):
        inst = FakeRollupTreeInstance()
        row = _base_rollup_row(
            hardware_key="board-1",
            test_platform="qemu",
            pass_tests=1,
        )

        process_rollup_summary(inst, row_dict=row, is_boot_row=True)

        assert inst.bootEnvironmentCompatible["board-1"]["PASS"] == 1
        assert "qemu" not in inst.bootEnvironmentMisc

    def test_misc_environment_when_hardware_matches_platform(self):
        inst = FakeRollupTreeInstance()
        row = _base_rollup_row(
            hardware_key="same",
            test_platform="same",
            fail_tests=1,
        )

        process_rollup_summary(inst, row_dict=row, is_boot_row=False)

        assert inst.testEnvironmentMisc["same"]["FAIL"] == 1

    def test_origin_and_lab_typed_summary(self):
        inst = FakeRollupTreeInstance()
        row = _base_rollup_row(
            test_origin="origin-x",
            test_lab="lab-y",
            error_tests=1,
        )

        process_rollup_summary(inst, row_dict=row, is_boot_row=False)

        origin = inst.test_summary["origins"]["origin-x"]
        assert origin.ERROR == 1
        lab = inst.test_summary_typed.labs["lab-y"]
        assert lab.ERROR == 1

    def test_accumulates_boot_counts_into_boot_summary(self):
        inst = FakeRollupTreeInstance()
        row = _base_rollup_row(pass_tests=3, fail_tests=2)

        process_rollup_summary(inst, row_dict=row, is_boot_row=True)

        assert inst.bootStatusSummary["PASS"] == 3
        assert inst.bootStatusSummary["FAIL"] == 2
        assert inst.bootPlatformsFailing == {"qemu"}
        arch_key = ("arm64", "gcc")
        assert inst.bootArchSummary[arch_key]["status"]["PASS"] == 3
        assert inst.bootConfigs["defconfig"]["PASS"] == 3


class TestProcessRollupIssues:
    def test_creates_issue_and_increments_failure_counts(self):
        inst = FakeRollupTreeInstance()
        row = _base_rollup_row(
            issue_id="bug-1",
            issue_version=1,
            issue_comment="c",
            issue_report_url="http://x",
            fail_tests=2,
            error_tests=1,
            miss_tests=0,
        )

        process_rollup_issues(inst, row_dict=row, is_boot_row=False)

        issue = inst.test_issues_dict[("bug-1", 1)]
        assert issue.comment == "c"
        assert issue.incidents_info.FAIL == 2
        assert issue.incidents_info.ERROR == 1

    def test_unknown_failures_respect_fail_status_filter(self):
        inst = FakeRollupTreeInstance()
        inst.filters.filterTestStatus = ["PASS"]
        row = _base_rollup_row(
            issue_id=None,
            issue_version=None,
            issue_uncategorized=True,
            fail_tests=4,
        )

        process_rollup_issues(inst, row_dict=row, is_boot_row=False)

        assert inst.failed_tests_with_unknown_issues == 0

    def test_unknown_failures_when_filter_allows_fail_or_empty(self):
        inst = FakeRollupTreeInstance()
        inst.filters.filterTestStatus = []
        row = _base_rollup_row(
            issue_id=None,
            issue_version=None,
            issue_uncategorized=True,
            fail_tests=3,
        )

        process_rollup_issues(inst, row_dict=row, is_boot_row=False)

        assert inst.failed_tests_with_unknown_issues == 3

    def test_boot_unknown_counter(self):
        inst = FakeRollupTreeInstance()
        row = _base_rollup_row(
            issue_id=None,
            issue_version=None,
            issue_uncategorized=True,
            fail_tests=2,
        )

        process_rollup_issues(inst, row_dict=row, is_boot_row=True)

        assert inst.failed_boots_with_unknown_issues == 2
