from http import HTTPStatus
import json
from unittest.mock import patch
from django.test import SimpleTestCase
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.typeModels.hardwareDetails import HardwareTestHistoryItem
from kernelCI_app.views.hardwareDetailsTestsView import HardwareDetailsTests
from rest_framework.test import APIRequestFactory


class TestHardwareDetailsTestsView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = HardwareDetailsTests()
        self.url = "/hardware/1/tests"

    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_trees_data")
    def test_post_hardware_details_tests_no_commits(self, mock_get_trees):
        mock_get_trees.return_value = []

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "selectedCommits": {},
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"error": ClientStrings.HARDWARE_NO_COMMITS})

    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_details_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_trees_with_selected_commit")
    def test_post_hardware_details_tests_not_found(
        self, mock_get_trees_selected, mock_get_trees, mock_get_details
    ):
        mock_tree = {
            "index": "tree1-branch1",
            "origin": "maestro",
            "tree_name": "tree1",
            "git_repository_branch": "branch1",
            "git_repository_url": "url1",
            "head_git_commit_name": "name1",
            "head_git_commit_hash": "hash1",
            "head_git_commit_tag": [],
            "selected_commit_status": None,
            "is_selected": True,
        }
        mock_get_trees.return_value = [mock_tree]
        mock_get_trees_selected.return_value = [mock_tree]
        mock_get_details.return_value = []

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "selectedCommits": {},
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.data, {"error": ClientStrings.HARDWARE_TEST_NOT_FOUND}
        )

    def test_post_hardware_details_tests_invalid_json_body(self):
        request = self.factory.post(
            self.url,
            data="invalid json",
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.data, {"error": ClientStrings.INVALID_JSON_BODY})

    def test_post_hardware_details_tests_invalid_timestamp(self):
        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": "invalid",
                    "endTimestampInSeconds": "invalid",
                    "selectedCommits": {},
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.data, {"error": ClientStrings.INVALID_TIMESTAMP})

    def test_post_hardware_details_tests_invalid_body_schema(self):
        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIsInstance(response.data, str)
        self.assertIn("selectedCommits", response.data)

    @patch.object(HardwareDetailsTests, "_sanitize_records")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_details_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_trees_with_selected_commit")
    def test_post_hardware_details_tests_response_validation_error(
        self,
        mock_get_trees_selected,
        mock_get_trees,
        mock_get_details,
        mock_sanitize_records,
    ):
        mock_tree = {
            "index": "tree1-branch1",
            "origin": "maestro",
            "tree_name": "tree1",
            "git_repository_branch": "branch1",
            "git_repository_url": "url1",
            "head_git_commit_name": "name1",
            "head_git_commit_hash": "hash1",
            "head_git_commit_tag": [],
            "selected_commit_status": None,
            "is_selected": True,
        }
        mock_get_trees.return_value = [mock_tree]
        mock_get_trees_selected.return_value = [mock_tree]
        mock_get_details.return_value = [
            {
                "id": "test1",
                "path": "test.path.name",
                "tree_name": "tree1",
                "git_commit_hash": "hash1",
                "git_repository_branch": "branch1",
            }
        ]

        mock_sanitize_records.side_effect = (
            lambda records, trees, is_all_selected: self.view.tests.append(
                {"invalid": "data"}
            )
        )

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "selectedCommits": {},
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, str)

    @patch("kernelCI_app.views.hardwareDetailsTestsView.unstable_parse_post_body")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_trees_with_selected_commit")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_details_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_boot")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_test_processed")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_test_in_filter")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.handle_test_history")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_validated_current_tree")
    @patch(
        "kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_full_record_filtered_out"
    )
    @patch("kernelCI_app.views.hardwareDetailsTestsView.assign_default_record_values")
    def test_post_processes_valid_test_successfully(
        self,
        mock_assign_default,
        mock_decide_filtered_out,
        mock_get_validated_tree,
        mock_handle_test_history,
        mock_decide_in_filter,
        mock_is_test_processed,
        mock_is_boot,
        mock_get_details,
        mock_get_trees_selected,
        mock_get_trees,
        mock_parse_body,
    ):
        mock_get_trees.return_value = [{"tree_name": "tree1"}]
        mock_get_trees_selected.return_value = [{"tree_name": "tree1"}]
        record = {"id": "test1", "path": "test.path.name"}
        mock_get_details.return_value = [record]

        mock_get_validated_tree.return_value = {"tree_name": "tree1"}
        mock_decide_filtered_out.return_value = False
        mock_is_boot.return_value = False
        mock_is_test_processed.return_value = False
        mock_decide_in_filter.return_value = True

        self.view.selected_commits = {}
        self.view.origin = "maestro"
        self.view.start_datetime = "start"
        self.view.end_datetime = "end"

        def side_effect_handle_test(record, task):
            task.append(
                HardwareTestHistoryItem(
                    id="test1",
                    status="PASS",
                    origin="maestro",
                    tree_name="tree1",
                    git_repository_branch="master",
                    duration=None,
                    path="test.path.name",
                    start_time=None,
                    environment_compatible=None,
                    config=None,
                    log_url=None,
                    architecture=None,
                    compiler=None,
                    environment_misc=None,
                    lab=None,
                )
            )

        mock_handle_test_history.side_effect = side_effect_handle_test

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "selectedCommits": {},
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.data,
            {
                "tests": [
                    {
                        "id": "test1",
                        "status": "PASS",
                        "origin": "maestro",
                        "tree_name": "tree1",
                        "git_repository_branch": "master",
                        "duration": None,
                        "path": "test.path.name",
                        "start_time": None,
                        "environment_compatible": None,
                        "config": None,
                        "log_url": None,
                        "architecture": None,
                        "compiler": None,
                        "environment_misc": None,
                        "lab": None,
                    }
                ]
            },
        )

        mock_parse_body.assert_called_once_with(instance=self.view, request=request)
        mock_get_trees.assert_called_once()
        mock_get_details.assert_called_once()
        mock_assign_default.assert_called_once_with(record)
        mock_is_boot.assert_called_once_with("test.path.name")
        mock_is_test_processed.assert_called_once()
        mock_decide_in_filter.assert_called_once()
        mock_handle_test_history.assert_called_once_with(
            record=record, task=self.view.tests
        )
        self.assertIn("test1", self.view.processed_tests)

    @patch("kernelCI_app.views.hardwareDetailsTestsView.unstable_parse_post_body")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_trees_with_selected_commit")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_details_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_boot")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_test_processed")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_test_in_filter")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.handle_test_history")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_validated_current_tree")
    @patch(
        "kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_full_record_filtered_out"
    )
    @patch("kernelCI_app.views.hardwareDetailsTestsView.assign_default_record_values")
    def test_post_skips_boot_records(
        self,
        mock_assign_default,
        mock_decide_filtered_out,
        mock_get_validated_tree,
        mock_handle_test_history,
        mock_decide_in_filter,
        mock_is_test_processed,
        mock_is_boot,
        mock_get_details,
        mock_get_trees_selected,
        mock_get_trees,
        mock_parse_body,
    ):
        mock_get_trees.return_value = [{"tree_name": "tree1"}]
        mock_get_trees_selected.return_value = [{"tree_name": "tree1"}]
        record = {"id": "test1", "path": "boot.path"}
        mock_get_details.return_value = [record]

        mock_get_validated_tree.return_value = {"tree_name": "tree1"}
        mock_decide_filtered_out.return_value = False
        mock_is_boot.return_value = True

        self.view.selected_commits = {}
        self.view.origin = "maestro"
        self.view.start_datetime = "start"
        self.view.end_datetime = "end"

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "selectedCommits": {},
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_parse_body.assert_called_once_with(instance=self.view, request=request)
        mock_assign_default.assert_called_once_with(record)
        mock_is_boot.assert_called_once_with("boot.path")
        mock_is_test_processed.assert_not_called()
        mock_decide_in_filter.assert_not_called()
        mock_handle_test_history.assert_not_called()

    @patch("kernelCI_app.views.hardwareDetailsTestsView.unstable_parse_post_body")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_trees_with_selected_commit")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_details_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_boot")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_test_processed")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_test_in_filter")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.handle_test_history")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_validated_current_tree")
    @patch(
        "kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_full_record_filtered_out"
    )
    @patch("kernelCI_app.views.hardwareDetailsTestsView.assign_default_record_values")
    def test_post_skips_already_processed_tests(
        self,
        mock_assign_default,
        mock_decide_filtered_out,
        mock_get_validated_tree,
        mock_handle_test_history,
        mock_decide_in_filter,
        mock_is_test_processed,
        mock_is_boot,
        mock_get_details,
        mock_get_trees_selected,
        mock_get_trees,
        mock_parse_body,
    ):
        mock_get_trees.return_value = [{"tree_name": "tree1"}]
        mock_get_trees_selected.return_value = [{"tree_name": "tree1"}]
        record = {"id": "test1", "path": "test.path"}
        mock_get_details.return_value = [record]

        mock_get_validated_tree.return_value = {"tree_name": "tree1"}
        mock_decide_filtered_out.return_value = False
        mock_is_boot.return_value = False
        mock_is_test_processed.return_value = True

        self.view.selected_commits = {}
        self.view.origin = "maestro"
        self.view.start_datetime = "start"
        self.view.end_datetime = "end"

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "selectedCommits": {},
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_parse_body.assert_called_once_with(instance=self.view, request=request)
        mock_assign_default.assert_called_once_with(record)
        mock_is_boot.assert_called_once_with("test.path")
        mock_is_test_processed.assert_called_once()
        mock_decide_in_filter.assert_not_called()
        mock_handle_test_history.assert_not_called()

    @patch("kernelCI_app.views.hardwareDetailsTestsView.unstable_parse_post_body")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_trees_with_selected_commit")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_details_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_boot")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_test_processed")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_test_in_filter")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.handle_test_history")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_validated_current_tree")
    @patch(
        "kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_full_record_filtered_out"
    )
    @patch("kernelCI_app.views.hardwareDetailsTestsView.assign_default_record_values")
    def test_post_skips_filtered_tests(
        self,
        mock_assign_default,
        mock_decide_filtered_out,
        mock_get_validated_tree,
        mock_handle_test_history,
        mock_decide_in_filter,
        mock_is_test_processed,
        mock_is_boot,
        mock_get_details,
        mock_get_trees_selected,
        mock_get_trees,
        mock_parse_body,
    ):
        mock_get_trees.return_value = [{"tree_name": "tree1"}]
        mock_get_trees_selected.return_value = [{"tree_name": "tree1"}]
        record = {"id": "test1", "path": "test.path"}
        mock_get_details.return_value = [record]

        mock_get_validated_tree.return_value = {"tree_name": "tree1"}
        mock_decide_filtered_out.return_value = False
        mock_is_boot.return_value = False
        mock_is_test_processed.return_value = False
        mock_decide_in_filter.return_value = False

        self.view.selected_commits = {}
        self.view.origin = "maestro"
        self.view.start_datetime = "start"
        self.view.end_datetime = "end"

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "selectedCommits": {},
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_parse_body.assert_called_once_with(instance=self.view, request=request)
        mock_assign_default.assert_called_once_with(record)
        mock_is_boot.assert_called_once_with("test.path")
        mock_is_test_processed.assert_called_once()
        mock_decide_in_filter.assert_called_once()
        mock_handle_test_history.assert_not_called()

    @patch("kernelCI_app.views.hardwareDetailsTestsView.unstable_parse_post_body")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_trees_with_selected_commit")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_details_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_boot")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_test_processed")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_test_in_filter")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.handle_test_history")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_validated_current_tree")
    @patch(
        "kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_full_record_filtered_out"
    )
    @patch("kernelCI_app.views.hardwareDetailsTestsView.assign_default_record_values")
    def test_post_skips_invalid_tree(
        self,
        mock_assign_default,
        mock_decide_filtered_out,
        mock_get_validated_tree,
        mock_handle_test_history,
        mock_decide_in_filter,
        mock_is_test_processed,
        mock_is_boot,
        mock_get_details,
        mock_get_trees_selected,
        mock_get_trees,
        mock_parse_body,
    ):
        mock_get_trees.return_value = [{"tree_name": "tree1"}]
        mock_get_trees_selected.return_value = [{"tree_name": "tree1"}]
        record = {"id": "test1", "path": "test.path"}
        mock_get_details.return_value = [record]

        mock_get_validated_tree.return_value = None

        self.view.selected_commits = {}
        self.view.origin = "maestro"
        self.view.start_datetime = "start"
        self.view.end_datetime = "end"

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "selectedCommits": {},
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_parse_body.assert_called_once_with(instance=self.view, request=request)
        mock_get_validated_tree.assert_called_once()
        mock_assign_default.assert_not_called()
        mock_decide_filtered_out.assert_not_called()
        mock_is_boot.assert_not_called()
        mock_is_test_processed.assert_not_called()
        mock_decide_in_filter.assert_not_called()
        mock_handle_test_history.assert_not_called()

    @patch("kernelCI_app.views.hardwareDetailsTestsView.unstable_parse_post_body")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_trees_with_selected_commit")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_hardware_details_data")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_boot")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.is_test_processed")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_test_in_filter")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.handle_test_history")
    @patch("kernelCI_app.views.hardwareDetailsTestsView.get_validated_current_tree")
    @patch(
        "kernelCI_app.views.hardwareDetailsTestsView.decide_if_is_full_record_filtered_out"
    )
    @patch("kernelCI_app.views.hardwareDetailsTestsView.assign_default_record_values")
    def test_post_skips_filtered_out_records(
        self,
        mock_assign_default,
        mock_decide_filtered_out,
        mock_get_validated_tree,
        mock_handle_test_history,
        mock_decide_in_filter,
        mock_is_test_processed,
        mock_is_boot,
        mock_get_details,
        mock_get_trees_selected,
        mock_get_trees,
        mock_parse_body,
    ):
        mock_get_trees.return_value = [{"tree_name": "tree1"}]
        mock_get_trees_selected.return_value = [{"tree_name": "tree1"}]
        record = {"id": "test1", "path": "test.path"}
        mock_get_details.return_value = [record]

        mock_get_validated_tree.return_value = {"tree_name": "tree1"}
        mock_decide_filtered_out.return_value = True

        self.view.selected_commits = {}
        self.view.origin = "maestro"
        self.view.start_datetime = "start"
        self.view.end_datetime = "end"

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "selectedCommits": {},
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_parse_body.assert_called_once_with(instance=self.view, request=request)
        mock_get_validated_tree.assert_called_once()
        mock_assign_default.assert_called_once_with(record)
        mock_decide_filtered_out.assert_called_once()
        mock_is_boot.assert_not_called()
        mock_is_test_processed.assert_not_called()
        mock_decide_in_filter.assert_not_called()
        mock_handle_test_history.assert_not_called()
