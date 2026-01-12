from http import HTTPStatus
import json
from unittest.mock import patch
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from pydantic import ValidationError
from kernelCI_app.views.hardwareDetailsBootsView import HardwareDetailsBoots
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.typeModels.hardwareDetails import HardwareTestHistoryItem


class TestHardwareDetailsBootsView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = HardwareDetailsBoots()
        self.url = "/hardware/hardware_id/boots"
        self.hardware_id = "test_hardware_id"

    @patch("kernelCI_app.views.hardwareDetailsBootsView.unstable_parse_post_body")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_trees_with_selected_commit")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_hardware_details_data")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.is_boot")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.is_test_processed")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.decide_if_is_test_in_filter")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.handle_test_history")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_validated_current_tree")
    @patch(
        "kernelCI_app.views.hardwareDetailsBootsView.decide_if_is_full_record_filtered_out"
    )
    @patch("kernelCI_app.views.hardwareDetailsBootsView.assign_default_record_values")
    def test_post_success(
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
        record = {"id": "record1", "path": "boot/path"}
        mock_get_details.return_value = [record]

        mock_get_validated_tree.return_value = {"tree_name": "tree1"}
        mock_decide_filtered_out.return_value = False
        mock_is_boot.return_value = True
        mock_is_test_processed.return_value = False
        mock_decide_in_filter.return_value = True

        self.view.selected_commits = {}
        self.view.origin = "test_origin"
        self.view.start_datetime = "start"
        self.view.end_datetime = "end"

        def side_effect_handle_test(record, task):
            task.append(
                HardwareTestHistoryItem(
                    id="boot1",
                    status="PASS",
                    origin="maestro",
                    tree_name="tree1",
                    git_repository_branch="master",
                    duration=None,
                    path=None,
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

        request = self.factory.post(self.url, data={"some": "data"}, format="json")
        response = self.view.post(request, self.hardware_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.data,
            {
                "boots": [
                    {
                        "id": "boot1",
                        "status": "PASS",
                        "origin": "maestro",
                        "tree_name": "tree1",
                        "git_repository_branch": "master",
                        "duration": None,
                        "path": None,
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
        mock_handle_test_history.assert_called_once()
        mock_assign_default.assert_called_once_with(record)

    @patch("kernelCI_app.views.hardwareDetailsBootsView.unstable_parse_post_body")
    def test_post_validation_error_body(self, mock_parse_body):
        mock_error = ValidationError.from_exception_data(
            "test_error", [{"type": "string_type", "loc": ("field",), "input": 123}]
        )
        mock_parse_body.side_effect = mock_error

        request = self.factory.post(self.url, data={}, format="json")
        response = self.view.post(request, self.hardware_id)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertTrue(isinstance(response.data, str))

    @patch("kernelCI_app.views.hardwareDetailsBootsView.unstable_parse_post_body")
    def test_post_json_decode_error(self, mock_parse_body):
        mock_parse_body.side_effect = json.JSONDecodeError("msg", "doc", 0)

        request = self.factory.post(self.url, data={}, format="json")
        response = self.view.post(request, self.hardware_id)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.data, {"error": ClientStrings.INVALID_JSON_BODY})

    @patch("kernelCI_app.views.hardwareDetailsBootsView.unstable_parse_post_body")
    def test_post_value_error(self, mock_parse_body):
        mock_parse_body.side_effect = ValueError("Invalid value")

        request = self.factory.post(self.url, data={}, format="json")
        response = self.view.post(request, self.hardware_id)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.data, {"error": ClientStrings.INVALID_TIMESTAMP})

    @patch("kernelCI_app.views.hardwareDetailsBootsView.unstable_parse_post_body")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_hardware_trees_data")
    def test_post_no_trees(self, mock_get_trees, mock_parse_body):
        mock_get_trees.return_value = []

        request = self.factory.post(self.url, data={}, format="json")
        response = self.view.post(request, self.hardware_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"error": ClientStrings.HARDWARE_NO_COMMITS})
        mock_parse_body.assert_called_once_with(instance=self.view, request=request)

    @patch("kernelCI_app.views.hardwareDetailsBootsView.unstable_parse_post_body")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_trees_with_selected_commit")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_hardware_details_data")
    def test_post_no_records(
        self, mock_get_details, mock_get_trees_selected, mock_get_trees, mock_parse_body
    ):
        mock_get_trees.return_value = [{"tree": "data"}]
        mock_get_trees_selected.return_value = [{"tree": "data"}]
        mock_get_details.return_value = []

        request = self.factory.post(self.url, data={}, format="json")
        response = self.view.post(request, self.hardware_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.data, {"error": ClientStrings.HARDWARE_BOOTS_NOT_FOUND}
        )
        mock_parse_body.assert_called_once_with(instance=self.view, request=request)

    @patch("kernelCI_app.views.hardwareDetailsBootsView.unstable_parse_post_body")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_hardware_trees_data")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_trees_with_selected_commit")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.get_hardware_details_data")
    @patch("kernelCI_app.views.hardwareDetailsBootsView.HardwareDetailsBootsResponse")
    def test_post_response_validation_error(
        self,
        mock_response_class,
        mock_get_details,
        mock_get_trees_selected,
        mock_get_trees,
        mock_parse_body,
    ):
        mock_get_trees.return_value = [{"tree": "data"}]
        mock_get_trees_selected.return_value = [{"tree": "data"}]
        mock_get_details.return_value = [{"record": "data"}]

        with patch.object(self.view, "_sanitize_records"):
            self.view.selected_commits = {}

            mock_error = ValidationError.from_exception_data(
                "test_error",
                [{"type": "string_type", "loc": ("boots",), "input": None}],
            )
            mock_response_class.side_effect = mock_error

            request = self.factory.post(self.url, data={}, format="json")
            response = self.view.post(request, self.hardware_id)

            self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
            self.assertTrue(isinstance(response.data, str))
            mock_parse_body.assert_called_once_with(instance=self.view, request=request)
