from kernelCI_app.typeModels.common import StatusCount
from unittest.mock import patch, MagicMock
from datetime import datetime
from collections import defaultdict
from kernelCI_app.helpers.hardwareDetails import (
    unstable_parse_post_body,
    set_trees_status_summary,
    get_displayed_commit,
    get_trees_with_selected_commit,
    get_arch_summary_typed,
    get_build_typed,
    get_tree_key,
    get_validated_current_tree,
    get_current_record_tree_in_selection,
    generate_test_dict,
    generate_build_summary_typed,
    generate_test_summary_typed,
    generate_tree_status_summary_dict,
    handle_tree_status_summary,
    create_record_test_platform,
    handle_test_history,
    handle_test_summary,
    handle_build_history,
    handle_build_summary,
    process_issue,
    update_issues,
    decide_if_is_full_record_filtered_out,
    decide_if_is_build_in_filter,
    get_processed_issue_key,
    is_issue_processed,
    is_test_processed,
    decide_if_is_test_in_filter,
    is_record_tree_selected,
    mutate_properties_to_list,
    assign_default_record_values,
    format_issue_summary_for_response,
    handle_build,
    process_filters,
    get_filter_options,
)
from kernelCI_app.typeModels.hardwareDetails import Tree
from kernelCI_app.typeModels.commonDetails import (
    TestArchSummaryItem,
    BuildSummary,
    TestSummary,
)
from kernelCI_app.constants.general import UNCATEGORIZED_STRING, UNKNOWN_STRING
from kernelCI_app.constants.hardwareDetails import SELECTED_HEAD_TREE_VALUE
from kernelCI_app.typeModels.databases import (
    build_fail_status_list,
)
from kernelCI_app.tests.unitTests.helpers.fixtures.hardware_details_data import (
    base_tree,
    tree_with_different_commit,
    base_tree_status_summary,
    create_test_summary,
    process_filters_instance,
    process_filters_instance_without_build,
    process_filters_record_with_build,
    process_filters_record_without_build,
    process_filters_record_boot,
    handle_test_summary_record_new_config,
    handle_test_summary_record_new_platform,
    handle_test_summary_record_new_origin,
)


class TestUnstableParsePostBody:
    @patch("kernelCI_app.helpers.hardwareDetails.FilterParams")
    def test_unstable_parse_post_body(self, mock_filter_params):
        """Test unstable_parse_post_body function."""
        mock_request = MagicMock()
        mock_request.body = (
            b'{"origin": "test", '
            b'"endTimestampInSeconds": 1640995200, '
            b'"startTimestampInSeconds": 1640908800, '
            b'"selectedCommits": {"1": "abc123"}}'
        )

        mock_instance = MagicMock()
        mock_filter_params.return_value = MagicMock()

        unstable_parse_post_body(instance=mock_instance, request=mock_request)

        assert mock_instance.origin == "test"
        assert isinstance(mock_instance.end_datetime, datetime)
        assert isinstance(mock_instance.start_datetime, datetime)
        assert mock_instance.selected_commits == {"1": "abc123"}
        mock_filter_params.assert_called_once()


class TestSetTreesStatusSummary:
    def test_set_trees_status_summary(self):
        """Test set_trees_status_summary function."""
        trees = [base_tree, tree_with_different_commit]
        tree_status_summary = base_tree_status_summary

        set_trees_status_summary(trees=trees, tree_status_summary=tree_status_summary)

        assert trees[0].selected_commit_status == {"builds": {"PASS": 5}}
        assert trees[1].selected_commit_status == {"builds": {"FAIL": 2}}


class TestGetDisplayedCommit:
    def test_get_displayed_commit_with_selected_commit(self):
        """Test get_displayed_commit with selected commit."""
        result = get_displayed_commit(tree=base_tree, selected_commit="def456")

        assert result == "def456"

    def test_get_displayed_commit_with_none_selected(self):
        """Test get_displayed_commit with None selected commit."""
        result = get_displayed_commit(tree=base_tree, selected_commit=None)

        assert result == "abc123"

    def test_get_displayed_commit_with_head_tree_value(self):
        """Test get_displayed_commit with SELECTED_HEAD_TREE_VALUE."""
        result = get_displayed_commit(
            tree=base_tree, selected_commit=SELECTED_HEAD_TREE_VALUE
        )

        assert result == "abc123"


class TestGetTreesWithSelectedCommit:
    def test_get_trees_with_selected_commit(self):
        """Test get_trees_with_selected_commit function."""
        trees = [base_tree, tree_with_different_commit]
        selected_commits = {"1": "custom123", "2": None}

        result = get_trees_with_selected_commit(
            trees=trees, selected_commits=selected_commits
        )

        assert len(result) == 2
        assert result[0].head_git_commit_hash == "custom123"
        assert result[0].is_selected is True
        assert result[1].head_git_commit_hash == "def456"
        assert result[1].is_selected is False


class TestGetArchSummaryTyped:
    def test_get_arch_summary_typed(self):
        """Test get_arch_summary_typed function."""
        record = {"build__architecture": "x86_64", "build__compiler": "gcc"}

        result = get_arch_summary_typed(record)

        assert isinstance(result, TestArchSummaryItem)
        assert result.arch == "x86_64"
        assert result.compiler == "gcc"
        assert isinstance(result.status, StatusCount)


class TestGetBuildTyped:
    def test_get_build_typed(self):
        """Test get_build_typed function."""
        record = {
            "build_id": "build123",
            "build__origin": "test",
            "build__architecture": "x86_64",
            "build__config_name": "defconfig",
            "build__misc": "{}",
            "build__config_url": "http://example.com/config",
            "build__compiler": "gcc",
            "build__status": "PASS",
            "build__duration": 100,
            "build__log_url": "http://example.com/log",
            "build__start_time": "2024-01-15T10:00:00Z",
            "build__checkout__git_repository_url": "https://git.kernel.org",
            "build__checkout__git_repository_branch": "master",
            "build__checkout__tree_name": "mainline",
            "build__incidents__issue__id": "issue123",
            "build__incidents__issue__version": 1,
        }

        result = get_build_typed(record, tree_idx=1)

        assert result.id == "build123"
        assert result.origin == "test"
        assert result.architecture == "x86_64"
        assert result.tree_name == "mainline"
        assert result.issue_id == "issue123"
        assert result.issue_version == 1


class TestGetTreeKey:
    def test_get_tree_key(self):
        """Test get_tree_key function."""
        record = {
            "build__checkout__tree_name": "mainline",
            "build__checkout__git_repository_branch": "master",
            "build__checkout__git_repository_url": "https://git.kernel.org",
        }

        result = get_tree_key(record)

        assert result == "mainlinemasterhttps://git.kernel.org"


class TestGetValidatedCurrentTree:
    @patch("kernelCI_app.helpers.hardwareDetails.DefaultRecordValues")
    @patch("kernelCI_app.helpers.hardwareDetails.get_current_record_tree_in_selection")
    @patch("kernelCI_app.helpers.hardwareDetails.log_message")
    def test_get_validated_current_tree_success(
        self, mock_log_message, mock_get_tree, mock_default_record
    ):
        """Test get_validated_current_tree with successful validation."""
        mock_default_record.return_value = MagicMock()
        mock_tree = MagicMock()
        mock_get_tree.return_value = mock_tree

        record = {"status": "PASS"}
        selected_trees = [mock_tree]

        result = get_validated_current_tree(
            record=record, selected_trees=selected_trees
        )

        assert result == mock_tree
        mock_log_message.assert_not_called()

    @patch("kernelCI_app.helpers.hardwareDetails.DefaultRecordValues")
    @patch("kernelCI_app.helpers.hardwareDetails.log_message")
    def test_get_validated_current_tree_validation_error(
        self, mock_log_message, mock_default_record
    ):
        """Test get_validated_current_tree with validation error."""
        from pydantic import ValidationError

        mock_default_record.side_effect = ValidationError.from_exception_data(
            "TestError", []
        )

        record = {"status": "INVALID"}
        selected_trees = []

        result = get_validated_current_tree(
            record=record, selected_trees=selected_trees
        )

        assert result is None
        mock_log_message.assert_called_once_with(f"Invalid row status for {record}")

    @patch("kernelCI_app.helpers.hardwareDetails.DefaultRecordValues")
    @patch("kernelCI_app.helpers.hardwareDetails.get_current_record_tree_in_selection")
    @patch("kernelCI_app.helpers.hardwareDetails.log_message")
    def test_get_validated_current_tree_no_tree_found(
        self, mock_log_message, mock_get_tree, mock_default_record
    ):
        """Test get_validated_current_tree with no tree found."""
        mock_default_record.return_value = MagicMock()
        mock_get_tree.return_value = None

        record = {"status": "PASS"}
        selected_trees = []

        result = get_validated_current_tree(
            record=record, selected_trees=selected_trees
        )

        assert result is None
        mock_log_message.assert_called_once_with(f"Tree not found for record: {record}")


class TestGetCurrentRecordTreeInSelection:
    def test_get_current_record_tree_in_selection_found(self):
        """Test get_current_record_tree_in_selection with matching tree."""
        record = {
            "build__checkout__tree_name": "mainline",
            "build__checkout__git_repository_branch": "master",
            "build__checkout__git_repository_url": "https://git.kernel.org",
            "build__checkout__origin": "test",
        }

        tree = Tree(
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

        selected_trees = [tree]

        result = get_current_record_tree_in_selection(
            record=record, selected_trees=selected_trees
        )

        assert result == tree

    def test_get_current_record_tree_in_selection_not_found(self):
        """Test get_current_record_tree_in_selection with no matching tree."""
        record = {
            "build__checkout__tree_name": "mainline",
            "build__checkout__git_repository_branch": "master",
            "build__checkout__git_repository_url": "https://git.kernel.org",
            "build__checkout__origin": "test",
        }

        tree = Tree(
            index="1",
            origin="test",
            tree_name="stable",
            git_repository_branch="linux-5.4.y",
            git_repository_url="https://git.kernel.org",
            head_git_commit_name="commit1",
            head_git_commit_hash="abc123",
            head_git_commit_tag=["v5.4"],
            selected_commit_status=None,
            is_selected=True,
        )

        selected_trees = [tree]

        result = get_current_record_tree_in_selection(
            record=record, selected_trees=selected_trees
        )

        assert result is None


class TestGenerateTestDict:
    def test_generate_test_dict(self):
        """Test generate_test_dict function."""
        result = generate_test_dict()

        assert result["history"] == []
        assert result["origins"] == {}
        assert result["archSummary"] == {}
        assert isinstance(result["platforms"], defaultdict)
        assert result["platformsFailing"] == set()
        assert isinstance(result["statusSummary"], defaultdict)
        assert isinstance(result["failReasons"], defaultdict)
        assert isinstance(result["configs"], defaultdict)
        assert result["issues"] == {}
        assert result["failedWithUnknownIssues"] == 0


class TestGenerateBuildSummaryTyped:
    def test_generate_build_summary_typed(self):
        """Test generate_build_summary_typed function."""
        result = generate_build_summary_typed()

        assert isinstance(result, BuildSummary)
        assert isinstance(result.status, StatusCount)
        assert result.origins == {}
        assert result.architectures == {}
        assert result.configs == {}
        assert result.issues == []
        assert result.unknown_issues == 0


class TestGenerateTestSummaryTyped:
    def test_generate_test_summary_typed(self):
        """Test generate_test_summary_typed function."""
        result = generate_test_summary_typed()

        assert isinstance(result, TestSummary)
        assert isinstance(result.status, StatusCount)
        assert result.origins == {}
        assert result.architectures == []
        assert result.configs == {}
        assert result.issues == []
        assert result.unknown_issues == 0
        assert result.fail_reasons == {}
        assert result.failed_platforms == set()


class TestGenerateTreeStatusSummaryDict:
    def test_generate_tree_status_summary_dict(self):
        """Test generate_tree_status_summary_dict function."""
        result = generate_tree_status_summary_dict()

        assert "builds" in result
        assert "boots" in result
        assert "tests" in result
        assert isinstance(result["builds"], defaultdict)
        assert isinstance(result["boots"], defaultdict)
        assert isinstance(result["tests"], defaultdict)


class TestHandleTreeStatusSummary:
    @patch("kernelCI_app.helpers.hardwareDetails.is_boot")
    def test_handle_tree_status_summary_boot(self, mock_is_boot):
        """Test handle_tree_status_summary with boot record."""
        mock_is_boot.return_value = True

        record = {
            "path": "boot.test",
            "status": "PASS",
            "build_id": "build123",
            "build__status": "PASS",
        }

        tree_status_summary = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        processed_builds = set()

        handle_tree_status_summary(
            record=record,
            tree_status_summary=tree_status_summary,
            tree_index="1",
            processed_builds=processed_builds,
        )

        assert tree_status_summary["1"]["boots"]["PASS"] == 1
        assert tree_status_summary["1"]["builds"]["PASS"] == 1

    @patch("kernelCI_app.helpers.hardwareDetails.is_boot")
    def test_handle_tree_status_summary_test(self, mock_is_boot):
        """Test handle_tree_status_summary with test record."""
        mock_is_boot.return_value = False

        record = {
            "path": "test.specific",
            "status": "FAIL",
            "build_id": "build123",
            "build__status": "PASS",
        }

        tree_status_summary = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        processed_builds = {"build123"}
        handle_tree_status_summary(
            record=record,
            tree_status_summary=tree_status_summary,
            tree_index="1",
            processed_builds=processed_builds,
        )

        assert tree_status_summary["1"]["tests"]["FAIL"] == 1
        assert tree_status_summary["1"]["builds"]["PASS"] == 0

    @patch("kernelCI_app.helpers.hardwareDetails.is_boot")
    def test_handle_tree_status_summary_with_missing_build_status(self, mock_is_boot):
        """Test handle_tree_status_summary with missing build__status."""
        mock_is_boot.return_value = False

        record = {
            "path": "test.specific",
            "status": "PASS",
            "build_id": "build123",
        }

        tree_status_summary = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        processed_builds = set()

        handle_tree_status_summary(
            record=record,
            tree_status_summary=tree_status_summary,
            tree_index="1",
            processed_builds=processed_builds,
        )

        assert tree_status_summary["1"]["tests"]["PASS"] == 1
        assert tree_status_summary["1"]["builds"]["NULL"] == 1


class TestCreateRecordTestPlatform:
    @patch("kernelCI_app.helpers.hardwareDetails.handle_misc")
    @patch("kernelCI_app.helpers.hardwareDetails.misc_value_or_default")
    def test_create_record_test_platform(
        self, mock_env_misc_value, mock_handle_env_misc
    ):
        """Test create_record_test_platform function."""
        mock_handle_env_misc.return_value = {"platform": "hp-x360-14a-cb0001xx-zork"}
        mock_env_misc_value.return_value = {"platform": "hp-x360-14a-cb0001xx-zork"}

        record = {"environment_misc": "{}"}

        result = create_record_test_platform(record=record)

        assert result == "hp-x360-14a-cb0001xx-zork"
        assert record["test_platform"] == "hp-x360-14a-cb0001xx-zork"
        mock_handle_env_misc.assert_called_once_with("{}")
        mock_env_misc_value.assert_called_once_with(
            {"platform": "hp-x360-14a-cb0001xx-zork"}
        )


class TestHandleTestHistory:
    @patch("kernelCI_app.helpers.hardwareDetails.create_record_test_platform")
    def test_handle_test_history(self, mock_create_platform):
        """Test handle_test_history function."""

        def mock_create_platform_side_effect(record):
            record["test_platform"] = "x86_64"
            return "x86_64"

        mock_create_platform.side_effect = mock_create_platform_side_effect

        record = {
            "id": "test123",
            "test_origin": "test",
            "status": "PASS",
            "duration": 100,
            "path": "test.specific",
            "start_time": "2024-01-15T10:00:00Z",
            "environment_compatible": "x86_64",
            "build__config_name": "defconfig",
            "log_url": "http://example.com/log",
            "build__architecture": "x86_64",
            "build__compiler": "gcc",
            "environment_misc": "{}",
            "build__checkout__tree_name": "mainline",
            "build__checkout__git_repository_branch": "master",
        }

        task = []

        handle_test_history(record=record, task=task)

        assert len(task) == 1
        assert task[0].id == "test123"
        assert task[0].status == "PASS"
        assert task[0].environment_misc.platform == "x86_64"
        mock_create_platform.assert_called_once_with(record=record)


class TestHandleTestSummary:
    @patch("kernelCI_app.helpers.hardwareDetails.process_issue")
    def test_handle_test_summary_with_null_status(self, mock_process_issue):
        """Test handle_test_summary with NULL status."""
        task = create_test_summary(
            status=StatusCount(DONE=0, PASS=0, FAIL=0, ERROR=0, SKIP=0, MISS=0, NULL=0)
        )
        record = {
            "status": None,
            "build__config_name": "defconfig",
            "build__architecture": "x86_64",
            "build__compiler": "gcc",
            "environment_misc": "{}",
            "misc": "{}",
            "test_origin": "test",
        }
        issue_dict = {}
        processed_archs = {}

        handle_test_summary(
            record=record,
            task=task,
            issue_dict=issue_dict,
            processed_archs=processed_archs,
        )

        mock_process_issue.assert_called_once()
        assert task.status.NULL == 1

    @patch("kernelCI_app.helpers.hardwareDetails.process_issue")
    def test_handle_test_summary_with_valid_status(self, mock_process_issue):
        """Test handle_test_summary with valid status."""
        task = create_test_summary(
            status=StatusCount(DONE=0, PASS=0, FAIL=0, ERROR=0, SKIP=0, MISS=0, NULL=0)
        )
        record = {
            "status": "PASS",
            "build__config_name": "defconfig",
            "build__architecture": "x86_64",
            "build__compiler": "gcc",
            "environment_misc": "{}",
            "misc": "{}",
            "test_origin": "test",
        }
        issue_dict = {}
        processed_archs = {}

        handle_test_summary(
            record=record,
            task=task,
            issue_dict=issue_dict,
            processed_archs=processed_archs,
        )

        mock_process_issue.assert_called_once()
        assert task.status.PASS == 1

    @patch("kernelCI_app.helpers.hardwareDetails.handle_misc")
    @patch("kernelCI_app.helpers.hardwareDetails.misc_value_or_default")
    @patch("kernelCI_app.helpers.hardwareDetails.is_status_failure")
    @patch("kernelCI_app.helpers.hardwareDetails.extract_error_message")
    @patch("kernelCI_app.helpers.hardwareDetails.process_issue")
    def test_handle_test_summary(
        self,
        mock_process_issue,
        mock_extract_error,
        mock_is_status_failure,
        mock_env_misc_value,
        mock_handle_env_misc,
    ):
        """Test handle_test_summary function."""
        mock_handle_env_misc.return_value = {"platform": "x86_64"}
        mock_env_misc_value.return_value = {"platform": "x86_64"}
        mock_is_status_failure.return_value = True
        mock_extract_error.return_value = "Test error"

        record = {
            "status": "FAIL",
            "build__config_name": "defconfig",
            "environment_misc": "{}",
            "build__architecture": "x86_64",
            "build__compiler": "gcc",
            "misc": "{}",
            "test_origin": "test",
        }

        task = TestSummary(
            status=StatusCount(),
            origins={},
            architectures=[],
            configs={},
            issues=[],
            unknown_issues=0,
            fail_reasons={},
            failed_platforms=set(),
            labs={},
        )

        issue_dict = {}
        processed_archs = {}

        handle_test_summary(
            record=record,
            task=task,
            issue_dict=issue_dict,
            processed_archs=processed_archs,
        )

        assert task.status.FAIL == 1
        assert "x86_64" in task.failed_platforms
        assert task.fail_reasons["Test error"] == 1
        mock_process_issue.assert_called_once()

    @patch("kernelCI_app.helpers.hardwareDetails.process_issue")
    def test_handle_test_summary_with_new_config(self, mock_process_issue):
        """Test handle_test_summary with new config."""
        task = create_test_summary(
            status=StatusCount(DONE=0, PASS=0, FAIL=0, ERROR=0, SKIP=0, MISS=0, NULL=0)
        )
        record = handle_test_summary_record_new_config
        issue_dict = {}
        processed_archs = {}

        handle_test_summary(
            record=record,
            task=task,
            issue_dict=issue_dict,
            processed_archs=processed_archs,
        )

        mock_process_issue.assert_called_once()
        assert "newconfig" in task.configs
        assert task.configs["newconfig"].PASS == 1
        assert task.status.PASS == 1

    @patch("kernelCI_app.helpers.hardwareDetails.process_issue")
    def test_handle_test_summary_with_new_platform(self, mock_process_issue):
        """Test handle_test_summary with new platform."""
        task = create_test_summary(
            status=StatusCount(DONE=0, PASS=0, FAIL=0, ERROR=0, SKIP=0, MISS=0, NULL=0)
        )
        record = handle_test_summary_record_new_platform
        issue_dict = {}
        processed_archs = {}

        handle_test_summary(
            record=record,
            task=task,
            issue_dict=issue_dict,
            processed_archs=processed_archs,
        )

        mock_process_issue.assert_called_once()
        assert "newplatform" in task.platforms
        assert task.platforms["newplatform"].FAIL == 1
        assert "newplatform" in task.failed_platforms
        assert "Test failed" in task.fail_reasons

    @patch("kernelCI_app.helpers.hardwareDetails.process_issue")
    def test_handle_test_summary_with_new_origin(self, mock_process_issue):
        """Test handle_test_summary with new origin."""
        task = create_test_summary(
            status=StatusCount(DONE=0, PASS=0, FAIL=0, ERROR=0, SKIP=0, MISS=0, NULL=0)
        )
        record = handle_test_summary_record_new_origin
        issue_dict = {}
        processed_archs = {}

        handle_test_summary(
            record=record,
            task=task,
            issue_dict=issue_dict,
            processed_archs=processed_archs,
        )

        mock_process_issue.assert_called_once()
        assert "neworigin" in task.origins
        assert task.origins["neworigin"].PASS == 1
        assert task.status.PASS == 1


class TestHandleBuildHistory:
    @patch("kernelCI_app.helpers.hardwareDetails.get_build_typed")
    def test_handle_build_history(self, mock_get_build_typed):
        """Test handle_build_history function."""
        mock_build = MagicMock()
        mock_get_build_typed.return_value = mock_build

        record = {"build_id": "build123"}
        builds = []

        handle_build_history(record=record, tree_idx=1, builds=builds)

        assert len(builds) == 1
        assert builds[0] == mock_build
        mock_get_build_typed.assert_called_once_with(record=record, tree_idx=1)


class TestHandleBuildSummary:
    @patch("kernelCI_app.helpers.hardwareDetails.get_build_typed")
    @patch("kernelCI_app.helpers.hardwareDetails.process_issue")
    def test_handle_build_summary(self, mock_process_issue, mock_get_build_typed):
        """Test handle_build_summary function."""
        mock_build = MagicMock()
        mock_build.status = "PASS"
        mock_build.config_name = "defconfig"
        mock_build.architecture = "x86_64"
        mock_build.compiler = "gcc"
        mock_build.origin = "test"
        mock_get_build_typed.return_value = mock_build

        record = {"build_id": "build123"}
        builds_summary = BuildSummary(
            status=StatusCount(),
            origins={},
            architectures={},
            configs={},
            issues=[],
            unknown_issues=0,
        )
        issue_dict = {}

        handle_build_summary(
            record=record,
            builds_summary=builds_summary,
            issue_dict=issue_dict,
            tree_index=1,
        )

        assert builds_summary.status.PASS == 1
        assert "defconfig" in builds_summary.configs
        assert "x86_64" in builds_summary.architectures
        assert "test" in builds_summary.origins
        mock_process_issue.assert_called_once()


class TestProcessIssue:
    @patch("kernelCI_app.helpers.hardwareDetails.is_status_failure")
    @patch("kernelCI_app.helpers.hardwareDetails.update_issues")
    def test_process_issue_build(self, mock_update_issues, mock_is_status_failure):
        """Test process_issue with build issue."""
        mock_is_status_failure.return_value = True

        record = {
            "build__status": "FAIL",
            "status": "PASS",  # Required field for process_issue
            "incidents__issue__id": "issue123",
            "incidents__issue__version": 1,
            "incidents__test_id": None,
            "incidents__issue__comment": "Test comment",
            "incidents__issue__report_url": "http://example.com",
        }

        task_issues_dict = {}

        process_issue(
            record=record, task_issues_dict=task_issues_dict, issue_from="build"
        )

        mock_is_status_failure.assert_called_once_with("FAIL", build_fail_status_list)
        mock_update_issues.assert_called_once()

    @patch("kernelCI_app.helpers.hardwareDetails.update_issues")
    def test_process_issue_test(self, mock_update_issues):
        """Test process_issue with test issue."""
        record = {
            "status": "FAIL",
            "build__status": "PASS",
            "incidents__issue__id": "issue123",
            "incidents__issue__version": 1,
            "incidents__test_id": "test123",
            "incidents__issue__comment": "Test comment",
            "incidents__issue__report_url": "http://example.com",
        }

        task_issues_dict = {}

        process_issue(
            record=record, task_issues_dict=task_issues_dict, issue_from="test"
        )

        mock_update_issues.assert_called_once()


class TestUpdateIssues:
    @patch("kernelCI_app.helpers.hardwareDetails.should_increment_build_issue")
    @patch("kernelCI_app.helpers.hardwareDetails.create_issue_typed")
    def test_update_issues_build_with_issue(
        self, mock_create_issue, mock_should_increment
    ):
        """Test update_issues with build issue."""
        mock_should_increment.return_value = ("issue123", 1, True)
        mock_issue = MagicMock()
        mock_create_issue.return_value = mock_issue

        task = {"issues": {}}

        update_issues(
            issue_id="issue123",
            issue_version=1,
            incident_test_id=None,
            build_status="FAIL",
            issue_comment="Test comment",
            issue_report_url="http://example.com",
            task=task,
            is_failed_task=True,
            issue_from="build",
        )

        assert ("issue123", 1) in task["issues"]
        mock_create_issue.assert_called_once()

    @patch("kernelCI_app.helpers.hardwareDetails.should_increment_build_issue")
    def test_update_issues_build_with_unknown_issue(self, mock_should_increment):
        """Test update_issues with build unknown issue."""
        mock_should_increment.return_value = (None, None, False)

        task = {"issues": {}, "failedWithUnknownIssues": 0}

        update_issues(
            issue_id=None,
            issue_version=None,
            incident_test_id=None,
            build_status="FAIL",
            test_status=None,
            issue_comment=None,
            issue_report_url=None,
            task=task,
            is_failed_task=True,
            issue_from="build",
        )

        assert task["failedWithUnknownIssues"] == 1

    @patch("kernelCI_app.helpers.hardwareDetails.should_increment_test_issue")
    def test_update_issues_test_with_unknown_issue(self, mock_should_increment):
        """Test update_issues with test unknown issue."""
        mock_should_increment.return_value = (None, None, False)

        task = {"issues": {}, "failedWithUnknownIssues": 0}

        update_issues(
            issue_id=None,
            issue_version=None,
            incident_test_id="test123",
            build_status="PASS",
            test_status="FAIL",
            issue_comment=None,
            issue_report_url=None,
            task=task,
            is_failed_task=True,
            issue_from="test",
        )

        assert task["failedWithUnknownIssues"] == 1

    @patch("kernelCI_app.helpers.hardwareDetails.should_increment_test_issue")
    @patch("kernelCI_app.helpers.hardwareDetails.create_issue_typed")
    def test_update_issues_test_with_issue(
        self, mock_create_issue, mock_should_increment
    ):
        """Test update_issues with test valid issue."""
        mock_should_increment.return_value = ("test_issue123", 1, True)
        mock_issue = MagicMock()
        mock_create_issue.return_value = mock_issue

        task = {"issues": {}}

        update_issues(
            issue_id="test_issue123",
            issue_version=1,
            incident_test_id="test123",
            build_status="PASS",
            test_status="FAIL",
            issue_comment="Test comment",
            issue_report_url="http://example.com",
            task=task,
            is_failed_task=True,
            issue_from="test",
        )

        assert ("test_issue123", 1) in task["issues"]
        mock_create_issue.assert_called_once_with(
            issue_id="test_issue123",
            issue_version=1,
            issue_comment="Test comment",
            issue_report_url="http://example.com",
            starting_count_status="FAIL",
        )

    @patch("kernelCI_app.helpers.hardwareDetails.should_increment_test_issue")
    def test_update_issues_with_existing_issue(self, mock_should_increment):
        """Test update_issues with existing issue."""
        task = {"issues": {}}
        existing_issue = MagicMock()
        existing_issue.incidents_info = MagicMock()
        task["issues"][("issue123", 1)] = existing_issue

        mock_should_increment.return_value = ("issue123", 1, True)

        update_issues(
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
            build_status="PASS",
            test_status="PASS",
            issue_comment="Test comment",
            issue_report_url="http://example.com",
            is_failed_task=True,
            issue_from="test",
            task=task,
        )

        existing_issue.incidents_info.increment.assert_called_once_with("PASS")


class TestDecideIfIsFullRecordFilteredOut:
    @patch("kernelCI_app.helpers.hardwareDetails.is_record_tree_selected")
    def test_decide_if_is_full_record_filtered_out_tree_not_selected(
        self, mock_is_selected
    ):
        """Test decide_if_is_full_record_filtered_out with tree not selected."""
        mock_is_selected.return_value = False

        instance = MagicMock()
        record = {
            "environment_compatible": ["hardware1"],
            "build__architecture": "x86_64",
            "build__compiler": "gcc",
            "build__config_name": "defconfig",
        }
        current_tree = MagicMock()

        result = decide_if_is_full_record_filtered_out(
            instance=instance,
            record=record,
            current_tree=current_tree,
            is_all_selected=False,
        )

        assert result is True
        mock_is_selected.assert_called_once()

    @patch("kernelCI_app.helpers.hardwareDetails.is_record_tree_selected")
    def test_decide_if_is_full_record_filtered_out_record_filtered(
        self, mock_is_selected
    ):
        """Test decide_if_is_full_record_filtered_out with record filtered."""
        mock_is_selected.return_value = True

        instance = MagicMock()
        instance.filters.is_record_filtered_out.return_value = True

        record = {
            "environment_compatible": ["hardware1"],
            "build__architecture": "x86_64",
            "build__compiler": "gcc",
            "build__config_name": "defconfig",
        }
        current_tree = MagicMock()

        result = decide_if_is_full_record_filtered_out(
            instance=instance,
            record=record,
            current_tree=current_tree,
            is_all_selected=False,
        )

        assert result is True
        instance.filters.is_record_filtered_out.assert_called_once()


class TestDecideIfIsBuildInFilter:

    def test_decide_if_is_build_in_filter(self):
        """Test decide_if_is_build_in_filter function."""
        instance = MagicMock()
        instance.filters.is_build_filtered_out.return_value = False

        build = MagicMock()
        build.id = "build123"
        build.status = "PASS"
        build.duration = 100
        build.issue_id = "issue123"
        build.issue_version = 1
        build.origin = "test"

        processed_builds = set()

        result = decide_if_is_build_in_filter(
            instance=instance,
            build=build,
            processed_builds=processed_builds,
            incident_test_id=None,
        )

        assert result is True
        instance.filters.is_build_filtered_out.assert_called_once()

    def test_decide_if_is_build_in_filter_with_dummy_build(self):
        """Test decide_if_is_build_in_filter with dummy build."""
        instance = MagicMock()
        instance.filters.is_build_filtered_out.return_value = False

        build = MagicMock()
        build.id = "maestro:dummy_123"
        build.status = "PASS"
        build.duration = 100
        build.issue_id = "issue123"
        build.issue_version = 1
        build.origin = "test"

        processed_builds = set()

        result = decide_if_is_build_in_filter(
            instance=instance,
            build=build,
            processed_builds=processed_builds,
            incident_test_id=None,
        )

        assert result is False
        instance.filters.is_build_filtered_out.assert_called_once()

    @patch("kernelCI_app.helpers.hardwareDetails.is_status_failure")
    def test_decide_if_is_build_in_filter_with_processed_build(
        self, mock_is_status_failure
    ):
        """Test decide_if_is_build_in_filter with processed build."""
        mock_is_status_failure.return_value = False

        instance = MagicMock()
        instance.filters.is_build_filtered_out.return_value = False

        build = MagicMock()
        build.id = "build123"
        build.status = "PASS"
        build.duration = 100
        build.issue_id = "issue123"
        build.issue_version = 1
        build.origin = "test"

        processed_builds = {"build123"}

        result = decide_if_is_build_in_filter(
            instance=instance,
            build=build,
            processed_builds=processed_builds,
            incident_test_id=None,
        )

        assert result is False
        instance.filters.is_build_filtered_out.assert_called_once()


class TestGetProcessedIssueKey:
    def test_get_processed_issue_key_with_issue(self):
        """Test get_processed_issue_key with issue."""
        record = {
            "id": "test123",
            "incidents__issue__id": "issue123",
            "incidents__issue__version": 1,
        }

        result = get_processed_issue_key(record=record)

        assert result == "test123issue1231"

    def test_get_processed_issue_key_with_none_issue(self):
        """Test get_processed_issue_key with None issue."""
        record = {
            "id": "test123",
            "incidents__issue__id": None,
            "incidents__issue__version": None,
        }

        result = get_processed_issue_key(record=record)

        assert result == "test123" + UNKNOWN_STRING + ""


class TestIsIssueProcessed:
    @patch("kernelCI_app.helpers.hardwareDetails.get_processed_issue_key")
    def test_is_issue_processed(self, mock_get_key):
        """Test is_issue_processed function."""
        mock_get_key.return_value = "test123issue1231"

        record = {"id": "test123"}
        processed_issues = {"test123issue1231"}

        result = is_issue_processed(record=record, processed_issues=processed_issues)

        assert result is True
        mock_get_key.assert_called_once_with(record=record)


class TestIsTestProcessed:
    def test_is_test_processed(self):
        """Test is_test_processed function."""
        record = {"id": "test123"}
        processed_tests = {"test123"}

        result = is_test_processed(record=record, processed_tests=processed_tests)

        assert result is True

    def test_is_test_not_processed(self):
        """Test is_test_processed with test not processed."""
        record = {"id": "test123"}
        processed_tests = {"test456"}

        result = is_test_processed(record=record, processed_tests=processed_tests)

        assert result is False


class TestDecideIfIsTestInFilter:
    @patch("kernelCI_app.helpers.hardwareDetails.misc_value_or_default")
    @patch("kernelCI_app.helpers.hardwareDetails.handle_misc")
    def test_decide_if_is_test_in_filter_boot(
        self, mock_handle_env_misc, mock_env_misc_value
    ):
        """Test decide_if_is_test_in_filter with boot test."""
        mock_handle_env_misc.return_value = {"platform": "x86_64"}
        mock_env_misc_value.return_value = {"platform": "x86_64"}

        instance = MagicMock()
        instance.filters.is_boot_filtered_out.return_value = False

        record = {
            "status": "PASS",
            "duration": 100,
            "path": "boot.test",
            "incidents__issue__id": "issue123",
            "incidents__issue__version": 1,
            "incidents__test_id": "test123",
            "environment_misc": "{}",
            "test_origin": "test",
        }

        result = decide_if_is_test_in_filter(
            instance=instance, test_type="boot", record=record
        )

        assert result is True
        instance.filters.is_boot_filtered_out.assert_called_once()

    @patch("kernelCI_app.helpers.hardwareDetails.misc_value_or_default")
    @patch("kernelCI_app.helpers.hardwareDetails.handle_misc")
    def test_decide_if_is_test_in_filter_test(
        self, mock_handle_env_misc, mock_env_misc_value
    ):
        """Test decide_if_is_test_in_filter with test."""
        mock_handle_env_misc.return_value = {"platform": "x86_64"}
        mock_env_misc_value.return_value = {"platform": "x86_64"}

        instance = MagicMock()
        instance.filters.is_test_filtered_out.return_value = False

        record = {
            "status": "PASS",
            "duration": 100,
            "path": "test.specific",
            "incidents__issue__id": "issue123",
            "incidents__issue__version": 1,
            "incidents__test_id": "test123",
            "environment_misc": "{}",
            "test_origin": "test",
        }

        result = decide_if_is_test_in_filter(
            instance=instance, test_type="test", record=record
        )

        assert result is True
        instance.filters.is_test_filtered_out.assert_called_once()


class TestIsRecordTreeSelected:
    def test_is_record_tree_selected_all_selected(self):
        """Test is_record_tree_selected with all selected."""
        record = {"build__checkout__git_commit_hash": "abc123"}
        tree = MagicMock()

        result = is_record_tree_selected(record=record, tree=tree, is_all_selected=True)

        assert result is True

    def test_is_record_tree_selected_tree_selected_and_matching_commit(self):
        """Test is_record_tree_selected with tree selected and matching commit."""
        record = {"build__checkout__git_commit_hash": "abc123"}
        tree = MagicMock()
        tree.is_selected = True
        tree.head_git_commit_hash = "abc123"

        result = is_record_tree_selected(
            record=record, tree=tree, is_all_selected=False
        )

        assert result is True

    def test_is_record_tree_selected_tree_not_selected(self):
        """Test is_record_tree_selected with tree not selected."""
        record = {"build__checkout__git_commit_hash": "abc123"}
        tree = MagicMock()
        tree.is_selected = False

        result = is_record_tree_selected(
            record=record, tree=tree, is_all_selected=False
        )

        assert result is False


class TestMutatePropertiesToList:
    def test_mutate_properties_to_list_with_dict(self):
        """Test mutate_properties_to_list with dict values."""
        test_dict = {"key1": {"a": 1, "b": 2}, "key2": {"c": 3, "d": 4}}

        mutate_properties_to_list(test_dict, ["key1", "key2"])

        assert test_dict["key1"] == [1, 2]
        assert test_dict["key2"] == [3, 4]

    def test_mutate_properties_to_list_with_set(self):
        """Test mutate_properties_to_list with set values."""
        test_dict = {"key1": {1, 2, 3}, "key2": {4, 5, 6}}

        mutate_properties_to_list(test_dict, ["key1", "key2"])

        assert set(test_dict["key1"]) == {1, 2, 3}
        assert set(test_dict["key2"]) == {4, 5, 6}


class TestAssignDefaultRecordValues:
    @patch("kernelCI_app.helpers.hardwareDetails.is_status_failure")
    def test_assign_default_record_values(self, mock_is_status_failure):
        """Test assign_default_record_values function."""
        mock_is_status_failure.return_value = True

        record = {
            "build__architecture": None,
            "build__compiler": None,
            "build__config_name": None,
            "build__incidents__issue__id": None,
            "build__status": "FAIL",
            "incidents__issue__id": None,
            "status": "FAIL",
        }

        assign_default_record_values(record)

        assert record["build__architecture"] == UNKNOWN_STRING
        assert record["build__compiler"] == UNKNOWN_STRING
        assert record["build__config_name"] == UNKNOWN_STRING
        assert record["build__incidents__issue__id"] == UNCATEGORIZED_STRING
        assert record["incidents__issue__id"] == UNCATEGORIZED_STRING


class TestFormatIssueSummaryForResponse:
    @patch("kernelCI_app.helpers.hardwareDetails.convert_issues_dict_to_list_typed")
    def test_format_issue_summary_for_response(self, mock_convert):
        """Test format_issue_summary_for_response function."""
        mock_issue1 = MagicMock()
        mock_issue2 = MagicMock()
        mock_issue3 = MagicMock()

        mock_convert.side_effect = [[mock_issue1], [mock_issue2], [mock_issue3]]

        builds_summary = BuildSummary(
            status=StatusCount(),
            origins={},
            architectures={},
            configs={},
            issues=[],
            unknown_issues=0,
        )
        boots_summary = TestSummary(
            status=StatusCount(),
            origins={},
            architectures=[],
            configs={},
            issues=[],
            unknown_issues=0,
            fail_reasons={},
            failed_platforms=set(),
            labs={},
        )
        tests_summary = TestSummary(
            status=StatusCount(),
            origins={},
            architectures=[],
            configs={},
            issues=[],
            unknown_issues=0,
            fail_reasons={},
            failed_platforms=set(),
            labs={},
        )

        issue_dicts = {
            "build": {"issues": {"issue1": MagicMock()}, "failedWithUnknownIssues": 5},
            "boot": {"issues": {"issue2": MagicMock()}, "failedWithUnknownIssues": 3},
            "test": {"issues": {"issue3": MagicMock()}, "failedWithUnknownIssues": 2},
        }

        format_issue_summary_for_response(
            builds_summary=builds_summary,
            boots_summary=boots_summary,
            tests_summary=tests_summary,
            issue_dicts=issue_dicts,
        )

        assert builds_summary.issues == [mock_issue1]
        assert boots_summary.issues == [mock_issue2]
        assert tests_summary.issues == [mock_issue3]
        assert builds_summary.unknown_issues == 5
        assert boots_summary.unknown_issues == 3
        assert tests_summary.unknown_issues == 2
        assert mock_convert.call_count == 3


class TestHandleBuildDeprecated:
    def test_handle_build_deprecated(self):
        """Test deprecated handle_build function."""
        instance = MagicMock()
        instance.builds = {"items": []}

        record = {
            "incidents__issue__id": "issue123",
            "incidents__issue__version": 1,
            "incidents__test_id": "test123",
            "build__status": "PASS",
            "status": "PASS",
            "incidents__issue__comment": "Test comment",
            "incidents__issue__report_url": "http://example.com",
        }

        build = {"id": "build123", "status": "PASS"}

        with patch(
            "kernelCI_app.helpers.hardwareDetails.update_issues"
        ) as mock_update_issues:
            handle_build(instance=instance, record=record, build=build)

            assert instance.builds["items"] == [build]
            mock_update_issues.assert_called_once()


class TestProcessRecordsWithFilters:
    def test_get_filter_options(self):
        """Test get_filter_options with filters."""
        instance = MagicMock()
        instance.global_configs = set()
        instance.global_architectures = set()
        instance.global_compilers = set()

        records = [
            {
                "build_id": "build123",
                "incidents__test_id": "test123",
                "build__incidents__issue__id": "issue123",
                "build__incidents__issue__version": 1,
                "build__status": "PASS",
                "build__config_name": "defconfig",
                "build__architecture": "x86_64",
                "build__compiler": "gcc",
            }
        ]

        selected_trees = [MagicMock()]

        with patch(
            "kernelCI_app.helpers.hardwareDetails.get_current_record_tree_in_selection"
        ) as mock_get_tree:
            with patch(
                "kernelCI_app.helpers.hardwareDetails.is_record_tree_selected"
            ) as mock_is_selected:
                with patch(
                    "kernelCI_app.helpers.hardwareDetails.process_filters"
                ) as mock_process_filters:
                    mock_get_tree.return_value = selected_trees[0]
                    mock_is_selected.return_value = True

                    get_filter_options(
                        instance=instance,
                        records=records,
                        selected_trees=selected_trees,
                        is_all_selected=True,
                    )

                    mock_process_filters.assert_called_once_with(
                        instance=instance, record=records[0]
                    )

    def test_process_records_with_filters_skip_record(self):
        """Test process_records with filters skipping record."""
        instance = MagicMock()
        records = [{"build_id": "build123"}]
        selected_trees = [MagicMock()]

        with patch(
            "kernelCI_app.helpers.hardwareDetails.get_current_record_tree_in_selection"
        ) as mock_get_tree:
            with patch(
                "kernelCI_app.helpers.hardwareDetails.is_record_tree_selected"
            ) as mock_is_selected:
                with patch(
                    "kernelCI_app.helpers.hardwareDetails.process_filters"
                ) as mock_process_filters:
                    mock_get_tree.return_value = None
                    mock_is_selected.return_value = False

                    get_filter_options(
                        instance=instance,
                        records=records,
                        selected_trees=selected_trees,
                        is_all_selected=True,
                    )

                    mock_process_filters.assert_not_called()


class TestProcessFilters:
    def test_process_filters_with_build_id(self):
        """Test process_filters with build_id."""
        instance = process_filters_instance
        record = process_filters_record_with_build

        with patch(
            "kernelCI_app.helpers.hardwareDetails.should_increment_build_issue"
        ) as mock_should_increment:
            with patch("kernelCI_app.helpers.hardwareDetails.add_unfiltered_issue"):
                mock_should_increment.return_value = ("issue123", 1, True)

                process_filters(instance=instance, record=record)

                assert "defconfig" in instance.global_configs
                assert "x86_64" in instance.global_architectures
                assert "gcc" in instance.global_compilers
                assert "test" in instance.unfiltered_origins["build"]

    def test_process_filters_without_build_id(self):
        """Test process_filters without build_id."""
        instance = process_filters_instance_without_build
        record = process_filters_record_without_build

        process_filters(instance=instance, record=record)

        assert len(instance.global_configs) == 0
        assert len(instance.global_architectures) == 0
        assert len(instance.global_compilers) == 0

    def test_process_filters_with_boot_record(self):
        """Test process_filters with boot record."""
        instance = process_filters_instance
        record = process_filters_record_boot

        with patch(
            "kernelCI_app.helpers.hardwareDetails.should_increment_test_issue"
        ) as mock_should_increment:
            with patch(
                "kernelCI_app.helpers.hardwareDetails.add_unfiltered_issue"
            ) as mock_add_unfiltered_issue:
                mock_should_increment.return_value = ("boot_issue123", 1, True)

                process_filters(instance=instance, record=record)

                mock_add_unfiltered_issue.assert_called_once()
                call_args = mock_add_unfiltered_issue.call_args
                assert call_args[1]["issue_set"] == instance.unfiltered_boot_issues
                assert call_args[1]["unknown_issue_flag_tab"] == "boot"
