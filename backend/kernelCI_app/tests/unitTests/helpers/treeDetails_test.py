from unittest.mock import patch, MagicMock
from kernelCI_app.helpers.treeDetails import (
    create_checkouts_where_clauses,
    get_current_row_data,
    process_tree_url,
    call_based_on_compatible_and_misc_platform,
    get_hardware_filter,
    get_build,
    process_builds_issue,
    process_tests_issue,
    decide_if_is_build_filtered_out,
    decide_if_is_boot_filtered_out,
    decide_if_is_full_row_filtered_out,
    decide_if_is_test_filtered_out,
    increment_test_origin_summary,
    process_test_summary,
    process_boots_summary,
    process_filters,
)
from kernelCI_app.typeModels.commonDetails import BuildHistoryItem
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.constants.general import (
    UNCATEGORIZED_STRING,
    UNKNOWN_STRING,
)
from kernelCI_app.typeModels.databases import NULL_STATUS
from kernelCI_app.tests.unitTests.helpers.fixtures.tree_details_data import (
    base_current_row,
    current_row_with_none_values,
    current_row_with_fail_status,
    base_row_data,
    row_data_with_unknown_compatible,
    build_only_row_data,
    test_only_row_data,
    combined_row_data,
)


class TestCreateCheckoutsWhereClauses:
    def test_create_checkouts_where_clauses_with_all_params(self):
        """Test create_checkouts_where_clauses with all parameters."""
        result = create_checkouts_where_clauses(
            git_url="https://git.kernel.org", git_branch="master", tree_name="mainline"
        )

        assert result["git_url_clause"] is None
        assert (
            result["git_branch_clause"]
            == "git_repository_branch = %(git_branch_param)s"
        )
        assert result["tree_name_clause"] == "tree_name = %(tree_name)s"

    def test_create_checkouts_where_clauses_with_url_and_branch(self):
        """Test create_checkouts_where_clauses with url and branch only."""
        result = create_checkouts_where_clauses(
            git_url="https://git.kernel.org", git_branch="master"
        )

        assert result["git_url_clause"] == "git_repository_url = %(git_url_param)s"
        assert (
            result["git_branch_clause"]
            == "git_repository_branch = %(git_branch_param)s"
        )
        assert result["tree_name_clause"] is None

    def test_create_checkouts_where_clauses_with_none_url(self):
        """Test create_checkouts_where_clauses with None url."""
        result = create_checkouts_where_clauses(git_url=None, git_branch="master")

        assert result["git_url_clause"] == "git_repository_url IS NULL"
        assert (
            result["git_branch_clause"]
            == "git_repository_branch = %(git_branch_param)s"
        )
        assert result["tree_name_clause"] is None

    def test_create_checkouts_where_clauses_with_none_branch(self):
        """Test create_checkouts_where_clauses with None branch."""
        result = create_checkouts_where_clauses(
            git_url="https://git.kernel.org", git_branch=None
        )

        assert result["git_url_clause"] == "git_repository_url = %(git_url_param)s"
        assert result["git_branch_clause"] == "git_repository_branch IS NULL"
        assert result["tree_name_clause"] is None

    def test_create_checkouts_where_clauses_with_none_values(self):
        """Test create_checkouts_where_clauses with None values."""
        result = create_checkouts_where_clauses(git_url=None, git_branch=None)

        assert result["git_url_clause"] == "git_repository_url IS NULL"
        assert result["git_branch_clause"] == "git_repository_branch IS NULL"
        assert result["tree_name_clause"] is None

    def test_create_checkouts_where_clauses_with_tree_name_and_none_branch(self):
        """Test create_checkouts_where_clauses with tree_name and None branch."""
        result = create_checkouts_where_clauses(
            tree_name="mainline", git_url=None, git_branch=None
        )

        assert result["git_url_clause"] == "git_repository_url IS NULL"
        assert result["git_branch_clause"] == "git_repository_branch IS NULL"
        assert result["tree_name_clause"] == "tree_name = %(tree_name)s"


class TestGetCurrentRowData:
    @patch("kernelCI_app.helpers.treeDetails.handle_misc")
    @patch("kernelCI_app.helpers.treeDetails.misc_value_or_default")
    @patch("kernelCI_app.helpers.treeDetails.extract_error_message")
    @patch("kernelCI_app.helpers.treeDetails.is_status_failure")
    def test_get_current_row_data(
        self,
        mock_is_status_failure,
        mock_extract_error,
        mock_misc_value,
        mock_handle_misc,
    ):
        """Test get_current_row_data function."""
        mock_handle_misc.return_value = {"platform": "x86_64"}
        mock_misc_value.return_value = {"platform": "x86_64"}
        mock_extract_error.return_value = "Test error"
        mock_is_status_failure.return_value = True

        result = get_current_row_data(base_current_row)

        assert result["test_id"] == "test123"
        assert result["test_origin"] == "test_origin"
        assert result["test_status"] == "PASS"
        assert result["test_platform"] == "x86_64"
        assert result["test_error"] == "Test error"
        assert result["build_status"] == "PASS"
        assert result["test_environment_compatible"] == "hardware1"
        assert result["build_architecture"] == "x86_64"
        assert result["build_compiler"] == "gcc"
        assert result["build_config_name"] == "defconfig"
        assert result["issue_id"] == "issue123"
        assert result["test_path"] == "test.path"
        assert result["history_item"]["id"] == "test123"
        assert result["history_item"]["status"] == "PASS"
        assert result["history_item"]["environment_misc"]["platform"] == "x86_64"

    @patch("kernelCI_app.helpers.treeDetails.handle_misc")
    @patch("kernelCI_app.helpers.treeDetails.misc_value_or_default")
    @patch("kernelCI_app.helpers.treeDetails.extract_error_message")
    @patch("kernelCI_app.helpers.treeDetails.is_status_failure")
    def test_get_current_row_data_with_none_values(
        self,
        mock_is_status_failure,
        mock_extract_error,
        mock_misc_value,
        mock_handle_misc,
    ):
        """Test get_current_row_data with None values."""
        mock_handle_misc.return_value = {"platform": "x86_64"}
        mock_misc_value.return_value = {"platform": "x86_64"}
        mock_extract_error.return_value = "Test error"
        mock_is_status_failure.return_value = True

        result = get_current_row_data(current_row_with_none_values)

        assert result["test_status"] == "NULL"
        assert result["build_status"] == NULL_STATUS
        assert result["test_environment_compatible"] == UNKNOWN_STRING
        assert result["build_architecture"] == UNKNOWN_STRING
        assert result["build_compiler"] == UNKNOWN_STRING
        assert result["build_config_name"] == UNKNOWN_STRING
        assert result["test_path"] == UNKNOWN_STRING

    @patch("kernelCI_app.helpers.treeDetails.handle_misc")
    @patch("kernelCI_app.helpers.treeDetails.misc_value_or_default")
    @patch("kernelCI_app.helpers.treeDetails.extract_error_message")
    @patch("kernelCI_app.helpers.treeDetails.is_status_failure")
    def test_get_current_row_data_with_failure_status(
        self,
        mock_is_status_failure,
        mock_extract_error,
        mock_misc_value,
        mock_handle_misc,
    ):
        """Test get_current_row_data with failure status."""
        mock_handle_misc.return_value = {"platform": "x86_64"}
        mock_misc_value.return_value = {"platform": "x86_64"}
        mock_extract_error.return_value = "Test error"
        mock_is_status_failure.return_value = True

        result = get_current_row_data(current_row_with_fail_status)

        assert result["issue_id"] == UNCATEGORIZED_STRING


class TestProcessTreeUrl:
    def test_process_tree_url_with_empty_url(self):
        """Test process_tree_url with empty tree_url."""
        instance = MagicMock()
        instance.tree_url = ""

        row_data = {"checkout_git_repository_url": "https://git.kernel.org"}

        process_tree_url(instance, row_data)

        assert instance.tree_url == "https://git.kernel.org"

    def test_process_tree_url_with_existing_url(self):
        """Test process_tree_url with existing tree_url."""
        instance = MagicMock()
        instance.tree_url = "https://existing.com"

        row_data = {"checkout_git_repository_url": "https://git.kernel.org"}

        process_tree_url(instance, row_data)

        assert instance.tree_url == "https://existing.com"

    def test_process_tree_url_with_none_url(self):
        """Test process_tree_url with None url."""
        instance = MagicMock()
        instance.tree_url = ""

        row_data = {"checkout_git_repository_url": None}

        process_tree_url(instance, row_data)

        assert instance.tree_url == ""


class TestCallBasedOnCompatibleAndMiscPlatform:
    @patch("kernelCI_app.helpers.treeDetails.misc_value_or_default")
    def test_call_based_on_compatible_and_misc_platform_with_compatible(
        self, mock_misc_value
    ):
        """Test call_based_on_compatible_and_misc_platform with compatible environment."""
        mock_misc_value.return_value = {"platform": "x86_64"}

        row_data = {
            "test_environment_compatible": "hardware1",
            "test_platform": "x86_64",
            "build_misc": {},
        }

        callback = MagicMock(return_value="result")

        result = call_based_on_compatible_and_misc_platform(row_data, callback)

        assert result == "result"
        callback.assert_called_once_with("hardware1")

    @patch("kernelCI_app.helpers.treeDetails.misc_value_or_default")
    def test_call_based_on_compatible_and_misc_platform_with_misc_platform(
        self, mock_misc_value
    ):
        """Test call_based_on_compatible_and_misc_platform with misc platform."""
        mock_misc_value.return_value = {"platform": "x86_64"}

        row_data = {
            "test_environment_compatible": UNKNOWN_STRING,
            "test_platform": "arm64",
            "build_misc": {},
        }

        callback = MagicMock(return_value="result")

        result = call_based_on_compatible_and_misc_platform(row_data, callback)

        assert result == "result"
        callback.assert_called_once_with("arm64")

    @patch("kernelCI_app.helpers.treeDetails.misc_value_or_default")
    def test_call_based_on_compatible_and_misc_platform_with_build_misc(
        self, mock_misc_value
    ):
        """Test call_based_on_compatible_and_misc_platform with build misc."""
        mock_misc_value.return_value = {"platform": "x86_64"}

        row_data = {
            "test_environment_compatible": UNKNOWN_STRING,
            "test_platform": UNKNOWN_STRING,
            "build_misc": {},
        }

        callback = MagicMock(return_value="result")

        result = call_based_on_compatible_and_misc_platform(row_data, callback)

        assert result == "result"
        callback.assert_called_once_with("x86_64")


class TestGetHardwareFilter:
    @patch(
        "kernelCI_app.helpers.treeDetails.call_based_on_compatible_and_misc_platform"
    )
    def test_get_hardware_filter(self, mock_call_based):
        """Test get_hardware_filter function."""
        mock_call_based.return_value = "hardware1"

        row_data = {
            "test_environment_compatible": "hardware1",
            "test_platform": "x86_64",
            "build_misc": {},
        }

        result = get_hardware_filter(row_data)

        assert result == "hardware1"
        mock_call_based.assert_called_once()


class TestGetBuild:
    def test_get_build(self):
        """Test get_build function."""
        row_data = {
            "build_id": "build123",
            "build_origin": "test",
            "build_architecture": "x86_64",
            "build_config_name": "defconfig",
            "build_misc": "{}",
            "build_config_url": "http://config.com",
            "build_compiler": "gcc",
            "build_status": "PASS",
            "build_duration": 100,
            "build_log_url": "http://log.com",
            "build_start_time": "2024-01-15T10:00:00Z",
            "checkout_git_repository_url": "https://git.kernel.org",
            "checkout_git_repository_branch": "master",
        }

        result = get_build(row_data)

        assert isinstance(result, BuildHistoryItem)
        assert result.id == "build123"
        assert result.origin == "test"
        assert result.architecture == "x86_64"
        assert result.config_name == "defconfig"
        assert result.status == "PASS"
        assert result.duration == 100
        assert result.git_repository_url == "https://git.kernel.org"
        assert result.git_repository_branch == "master"


class TestProcessBuildsIssue:
    @patch("kernelCI_app.helpers.treeDetails.should_increment_build_issue")
    @patch("kernelCI_app.helpers.treeDetails.create_issue_typed")
    def test_process_builds_issue_with_new_issue(
        self, mock_create_issue, mock_should_increment
    ):
        """Test process_builds_issue with new issue."""
        mock_should_increment.return_value = ("issue123", 1, True)
        mock_issue = MagicMock()
        mock_create_issue.return_value = mock_issue

        instance = MagicMock()
        instance.build_issues_dict = {}
        instance.processed_builds = set()

        row_data = {
            "build_id": "build123",
            "issue_id": "issue123",
            "issue_comment": "Test comment",
            "issue_report_url": "http://example.com",
            "issue_version": 1,
            "build_status": "FAIL",
            "incident_test_id": None,
        }

        process_builds_issue(instance=instance, row_data=row_data)

        assert ("issue123", 1) in instance.build_issues_dict
        mock_create_issue.assert_called_once()

    @patch("kernelCI_app.helpers.treeDetails.should_increment_build_issue")
    def test_process_builds_issue_with_existing_issue(self, mock_should_increment):
        """Test process_builds_issue with existing issue."""
        mock_should_increment.return_value = ("issue123", 1, True)

        existing_issue = MagicMock()
        instance = MagicMock()
        instance.build_issues_dict = {("issue123", 1): existing_issue}
        instance.processed_builds = set()

        row_data = {
            "build_id": "build123",
            "issue_id": "issue123",
            "issue_comment": "Test comment",
            "issue_report_url": "http://example.com",
            "issue_version": 1,
            "build_status": "FAIL",
            "incident_test_id": None,
        }

        process_builds_issue(instance=instance, row_data=row_data)

        existing_issue.incidents_info.increment.assert_called_once_with("FAIL")

    @patch("kernelCI_app.helpers.treeDetails.should_increment_build_issue")
    def test_process_builds_issue_with_unknown_issue(self, mock_should_increment):
        """Test process_builds_issue with unknown issue."""
        mock_should_increment.return_value = (None, None, False)

        instance = MagicMock()
        instance.build_issues_dict = {}
        instance.processed_builds = set()
        instance.failed_builds_with_unknown_issues = 0

        row_data = {
            "build_id": "build123",
            "issue_id": None,
            "issue_comment": None,
            "issue_report_url": None,
            "issue_version": None,
            "build_status": "FAIL",
            "incident_test_id": None,
        }

        process_builds_issue(instance=instance, row_data=row_data)

        assert instance.failed_builds_with_unknown_issues == 1


class TestProcessTestsIssue:
    @patch("kernelCI_app.helpers.treeDetails.should_increment_test_issue")
    @patch("kernelCI_app.helpers.treeDetails.create_issue_typed")
    def test_process_tests_issue_with_new_issue(
        self, mock_create_issue, mock_should_increment
    ):
        """Test process_tests_issue with new issue."""
        mock_should_increment.return_value = ("issue123", 1, True)
        mock_issue = MagicMock()
        mock_create_issue.return_value = mock_issue

        instance = MagicMock()
        instance.test_issues_dict = {}
        instance.failed_tests_with_unknown_issues = 0

        row_data = {
            "test_status": "FAIL",
            "issue_id": "issue123",
            "issue_comment": "Test comment",
            "issue_version": 1,
            "issue_report_url": "http://example.com",
            "incident_test_id": "test123",
        }

        process_tests_issue(instance=instance, row_data=row_data, is_boot=False)

        assert ("issue123", 1) in instance.test_issues_dict
        mock_create_issue.assert_called_once()

    @patch("kernelCI_app.helpers.treeDetails.should_increment_test_issue")
    def test_process_tests_issue_with_boot(self, mock_should_increment):
        """Test process_tests_issue with boot."""
        mock_should_increment.return_value = ("issue123", 1, True)

        instance = MagicMock()
        instance.boot_issues_dict = {}
        instance.failed_boots_with_unknown_issues = 0

        row_data = {
            "test_status": "FAIL",
            "issue_id": "issue123",
            "issue_comment": "Test comment",
            "issue_version": 1,
            "issue_report_url": "http://example.com",
            "incident_test_id": "test123",
        }

        process_tests_issue(instance=instance, row_data=row_data, is_boot=True)

        assert ("issue123", 1) in instance.boot_issues_dict

    @patch("kernelCI_app.helpers.treeDetails.should_increment_test_issue")
    def test_process_tests_issue_with_unknown_issue(self, mock_should_increment):
        """Test process_tests_issue with unknown issue."""
        mock_should_increment.return_value = (None, None, False)

        instance = MagicMock()
        instance.test_issues_dict = {}
        instance.failed_tests_with_unknown_issues = 0

        row_data = {
            "test_status": "FAIL",
            "issue_id": None,
            "issue_comment": None,
            "issue_version": None,
            "issue_report_url": None,
            "incident_test_id": "test123",
        }

        process_tests_issue(instance=instance, row_data=row_data, is_boot=False)

        assert instance.failed_tests_with_unknown_issues == 1

    @patch("kernelCI_app.helpers.treeDetails.should_increment_test_issue")
    @patch("kernelCI_app.helpers.treeDetails.create_issue_typed")
    def test_process_tests_issue_with_existing_issue(
        self, mock_create_issue, mock_should_increment
    ):
        """Test process_tests_issue with existing issue."""
        mock_should_increment.return_value = ("issue123", 1, True)

        existing_issue = MagicMock()
        instance = MagicMock()
        instance.test_issues_dict = {("issue123", 1): existing_issue}
        instance.failed_tests_with_unknown_issues = 0

        row_data = {
            "test_status": "FAIL",
            "issue_id": "issue123",
            "issue_comment": "Test comment",
            "issue_version": 1,
            "issue_report_url": "http://example.com",
            "incident_test_id": "test123",
        }

        process_tests_issue(instance=instance, row_data=row_data, is_boot=False)

        existing_issue.incidents_info.increment.assert_called_once_with("FAIL")
        mock_create_issue.assert_not_called()

    @patch("kernelCI_app.helpers.treeDetails.should_increment_test_issue")
    def test_process_tests_issue_with_unknown_issue_boot(self, mock_should_increment):
        """Test process_tests_issue with unknown issue for boot."""
        mock_should_increment.return_value = (None, None, False)

        instance = MagicMock()
        instance.boot_issues_dict = {}
        instance.failed_boots_with_unknown_issues = 0

        row_data = {
            "test_status": "FAIL",
            "issue_id": None,
            "issue_comment": None,
            "issue_version": None,
            "issue_report_url": None,
            "incident_test_id": "test123",
        }

        process_tests_issue(instance=instance, row_data=row_data, is_boot=True)

        assert instance.failed_boots_with_unknown_issues == 1


class TestDecideIfIsBuildFilteredOut:
    def test_decide_if_is_build_filtered_out(self):
        """Test decide_if_is_build_filtered_out function."""
        instance = MagicMock()
        instance.filters.is_build_filtered_out.return_value = True

        row_data = {
            "issue_id": "issue123",
            "issue_version": 1,
            "build_status": "FAIL",
            "build_duration": 100,
            "incident_test_id": "test123",
            "build_origin": "test",
        }

        result = decide_if_is_build_filtered_out(instance, row_data)

        assert result is True
        instance.filters.is_build_filtered_out.assert_called_once_with(
            build_status="FAIL",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
            build_origin="test",
        )


class TestDecideIfIsBootFilteredOut:
    def test_decide_if_is_boot_filtered_out(self):
        """Test decide_if_is_boot_filtered_out function."""
        instance = MagicMock()
        instance.filters.is_boot_filtered_out.return_value = True

        row_data = {
            "test_status": "FAIL",
            "test_duration": 100,
            "issue_id": "issue123",
            "issue_version": 1,
            "test_path": "boot.test",
            "incident_test_id": "test123",
            "test_origin": "test",
        }

        result = decide_if_is_boot_filtered_out(instance, row_data)

        assert result is True
        instance.filters.is_boot_filtered_out.assert_called_once_with(
            duration=100,
            issue_id="issue123",
            issue_version=1,
            path="boot.test",
            status="FAIL",
            incident_test_id="test123",
            origin="test",
        )


class TestDecideIfIsFullRowFilteredOut:
    @patch("kernelCI_app.helpers.treeDetails.get_hardware_filter")
    def test_decide_if_is_full_row_filtered_out(self, mock_get_hardware_filter):
        """Test decide_if_is_full_row_filtered_out function."""
        mock_get_hardware_filter.return_value = "hardware1"

        instance = MagicMock()
        instance.filters.is_record_filtered_out.return_value = True

        row_data = {
            "build_architecture": "x86_64",
            "build_compiler": "gcc",
            "build_config_name": "defconfig",
            "history_item": {
                "lab": "test_lab",
            },
        }

        result = decide_if_is_full_row_filtered_out(instance, row_data)

        assert result is True
        instance.filters.is_record_filtered_out.assert_called_once_with(
            hardwares=["hardware1"],
            architecture="x86_64",
            compiler="gcc",
            config_name="defconfig",
            lab="test_lab",
        )


class TestDecideIfIsTestFilteredOut:
    def test_decide_if_is_test_filtered_out(self):
        """Test decide_if_is_test_filtered_out function."""
        instance = MagicMock()
        instance.filters.is_test_filtered_out.return_value = True

        row_data = {
            "test_status": "FAIL",
            "test_duration": 100,
            "issue_id": "issue123",
            "issue_version": 1,
            "test_path": "test.specific",
            "incident_test_id": "test123",
            "test_origin": "test",
        }

        result = decide_if_is_test_filtered_out(instance, row_data)

        assert result is True
        instance.filters.is_test_filtered_out.assert_called_once_with(
            duration=100,
            issue_id="issue123",
            issue_version=1,
            path="test.specific",
            status="FAIL",
            incident_test_id="test123",
            origin="test",
        )


class TestIncrementTestOriginSummary:
    def test_increment_test_origin_summary_new_origin(self):
        """Test increment_test_origin_summary with new origin."""
        origin_summary = {}

        increment_test_origin_summary("test_origin", "PASS", origin_summary)

        assert "test_origin" in origin_summary
        assert isinstance(origin_summary["test_origin"], StatusCount)
        assert origin_summary["test_origin"].PASS == 1

    def test_increment_test_origin_summary_existing_origin(self):
        """Test increment_test_origin_summary with existing origin."""
        origin_summary = {"test_origin": StatusCount()}
        origin_summary["test_origin"].PASS = 5

        increment_test_origin_summary("test_origin", "PASS", origin_summary)

        assert origin_summary["test_origin"].PASS == 6

    def test_increment_test_origin_summary_different_status(self):
        """Test increment_test_origin_summary with different status."""
        origin_summary = {"test_origin": StatusCount()}
        origin_summary["test_origin"].PASS = 5

        increment_test_origin_summary("test_origin", "FAIL", origin_summary)

        assert origin_summary["test_origin"].PASS == 5
        assert origin_summary["test_origin"].FAIL == 1


class TestProcessTestSummary:
    @patch("kernelCI_app.helpers.treeDetails.is_status_failure")
    def test_process_test_summary(self, mock_is_status_failure):
        """Test process_test_summary function."""
        mock_is_status_failure.return_value = True

        instance = MagicMock()
        instance.testStatusSummary = {}
        instance.test_arch_summary = {}
        instance.test_configs = {}
        instance.testPlatformsWithErrors = set()
        instance.testFailReasons = {}
        instance.testEnvironmentCompatible = {
            "hardware1": {
                "FAIL": 0,
                "PASS": 0,
                "SKIP": 0,
                "ERROR": 0,
                "MISS": 0,
                "NULL": 0,
                "DONE": 0,
            },
        }
        instance.testEnvironmentMisc = {}
        instance.test_summary = {"origins": {}}

        process_test_summary(instance, base_row_data)

        assert instance.testStatusSummary["FAIL"] == 1
        assert "x86_64-gcc" in instance.test_arch_summary
        assert "defconfig" in instance.test_configs
        assert "x86_64" in instance.testPlatformsWithErrors
        assert instance.testFailReasons["Test error"] == 1
        assert instance.testEnvironmentCompatible["hardware1"]["FAIL"] == 1

    @patch("kernelCI_app.helpers.treeDetails.is_status_failure")
    def test_process_test_summary_with_unknown_compatible(self, mock_is_status_failure):
        """Test process_test_summary with unknown compatible environment.

        This test differs from the base test in that it uses UNKNOWN_STRING for
        test_environment_compatible instead of a specific hardware value.
        This causes the test to be tracked in testEnvironmentMisc instead of
        testEnvironmentCompatible, simulating scenarios where the environment
        compatibility is unknown or not specified.
        """
        mock_is_status_failure.return_value = False

        instance = MagicMock()
        instance.testStatusSummary = {}
        instance.test_arch_summary = {}
        instance.test_configs = {}
        instance.testPlatformsWithErrors = set()
        instance.testFailReasons = {}
        instance.testEnvironmentCompatible = {}
        instance.testEnvironmentMisc = {
            "x86_64": {
                "FAIL": 0,
                "PASS": 0,
                "SKIP": 0,
                "ERROR": 0,
                "MISS": 0,
                "NULL": 0,
                "DONE": 0,
            },
        }
        instance.test_summary = {"origins": {}}

        process_test_summary(instance, row_data_with_unknown_compatible)

        assert instance.testStatusSummary["PASS"] == 1
        assert instance.testEnvironmentMisc["x86_64"]["PASS"] == 1


class TestProcessBootsSummary:
    @patch("kernelCI_app.helpers.treeDetails.is_status_failure")
    def test_process_boots_summary(self, mock_is_status_failure):
        """Test process_boots_summary function."""
        mock_is_status_failure.return_value = True

        instance = MagicMock()
        instance.bootStatusSummary = {}
        instance.bootArchSummary = {}
        instance.bootConfigs = {}
        instance.bootPlatformsFailing = set()
        instance.bootFailReasons = {}
        instance.bootEnvironmentCompatible = {
            "hardware1": {
                "FAIL": 0,
                "PASS": 0,
                "SKIP": 0,
                "ERROR": 0,
                "MISS": 0,
                "NULL": 0,
                "DONE": 0,
            },
        }
        instance.bootEnvironmentMisc = {}
        instance.boot_summary = {"origins": {}}

        process_boots_summary(instance, base_row_data)

        assert instance.bootStatusSummary["FAIL"] == 1
        assert "x86_64-gcc" in instance.bootArchSummary
        assert "defconfig" in instance.bootConfigs
        assert "x86_64" in instance.bootPlatformsFailing
        assert instance.bootFailReasons["Test error"] == 1
        assert instance.bootEnvironmentCompatible["hardware1"]["FAIL"] == 1

    @patch("kernelCI_app.helpers.treeDetails.is_status_failure")
    def test_process_boots_summary_with_unknown_compatible(
        self, mock_is_status_failure
    ):
        """Test process_boots_summary with unknown compatible environment.

        This test differs from the base test in that it uses UNKNOWN_STRING for
        test_environment_compatible instead of a specific hardware value.
        This causes the boot to be tracked in bootEnvironmentMisc instead of
        bootEnvironmentCompatible, simulating scenarios where the environment
        compatibility is unknown or not specified.
        """
        mock_is_status_failure.return_value = False

        instance = MagicMock()
        instance.bootStatusSummary = {}
        instance.bootArchSummary = {}
        instance.bootConfigs = {}
        instance.bootPlatformsFailing = set()
        instance.bootFailReasons = {}
        instance.bootEnvironmentCompatible = {}
        instance.bootEnvironmentMisc = {
            "x86_64": {
                "FAIL": 0,
                "PASS": 0,
                "SKIP": 0,
                "ERROR": 0,
                "MISS": 0,
                "NULL": 0,
                "DONE": 0,
            },
        }
        instance.boot_summary = {"origins": {}}

        process_boots_summary(instance, row_data_with_unknown_compatible)

        assert instance.bootStatusSummary["PASS"] == 1
        assert instance.bootEnvironmentMisc["x86_64"]["PASS"] == 1


class TestProcessFilters:
    @patch("kernelCI_app.helpers.treeDetails.should_increment_build_issue")
    @patch("kernelCI_app.helpers.treeDetails.should_increment_test_issue")
    @patch("kernelCI_app.helpers.treeDetails.add_unfiltered_issue")
    @patch("kernelCI_app.helpers.treeDetails.is_boot")
    def test_process_filters_with_build_and_test(
        self,
        mock_is_boot,
        mock_add_unfiltered_issue,
        mock_should_increment_test,
        mock_should_increment_build,
    ):
        """Test process_filters with both build and test."""
        mock_should_increment_build.return_value = ("issue123", 1, True)
        mock_should_increment_test.return_value = ("issue456", 2, True)
        mock_is_boot.return_value = False

        instance = MagicMock()
        instance.global_configs = set()
        instance.global_architectures = set()
        instance.global_compilers = set()
        instance.unfiltered_origins = {"build": set(), "test": set()}
        instance.unfiltered_build_issues = set()
        instance.unfiltered_test_issues = set()
        instance.unfiltered_uncategorized_issue_flags = {"build": False, "test": False}

        process_filters(instance, combined_row_data)

        assert "defconfig" in instance.global_configs
        assert "x86_64" in instance.global_architectures
        assert "gcc" in instance.global_compilers
        assert "build_origin" in instance.unfiltered_origins["build"]
        assert "test_origin" in instance.unfiltered_origins["test"]
        assert mock_add_unfiltered_issue.call_count == 2

    @patch("kernelCI_app.helpers.treeDetails.should_increment_build_issue")
    @patch("kernelCI_app.helpers.treeDetails.add_unfiltered_issue")
    def test_process_filters_with_build_only(
        self, mock_add_unfiltered_issue, mock_should_increment_build
    ):
        """Test process_filters with build only."""
        mock_should_increment_build.return_value = ("issue123", 1, True)

        instance = MagicMock()
        instance.global_configs = set()
        instance.global_architectures = set()
        instance.global_compilers = set()
        instance.unfiltered_origins = {"build": set()}
        instance.unfiltered_build_issues = set()
        instance.unfiltered_uncategorized_issue_flags = {"build": False}

        process_filters(instance, build_only_row_data)

        assert "defconfig" in instance.global_configs
        assert "x86_64" in instance.global_architectures
        assert "gcc" in instance.global_compilers
        assert "build_origin" in instance.unfiltered_origins["build"]
        mock_add_unfiltered_issue.assert_called_once()

    @patch("kernelCI_app.helpers.treeDetails.should_increment_test_issue")
    @patch("kernelCI_app.helpers.treeDetails.add_unfiltered_issue")
    @patch("kernelCI_app.helpers.treeDetails.is_boot")
    def test_process_filters_with_test_only(
        self, mock_is_boot, mock_add_unfiltered_issue, mock_should_increment_test
    ):
        """Test process_filters with test only."""
        mock_should_increment_test.return_value = ("issue456", 2, True)
        mock_is_boot.return_value = True

        instance = MagicMock()
        instance.unfiltered_origins = {"boot": set()}
        instance.unfiltered_boot_issues = set()
        instance.unfiltered_uncategorized_issue_flags = {"boot": False}

        process_filters(instance, test_only_row_data)

        assert "test_origin" in instance.unfiltered_origins["boot"]
        mock_add_unfiltered_issue.assert_called_once()
