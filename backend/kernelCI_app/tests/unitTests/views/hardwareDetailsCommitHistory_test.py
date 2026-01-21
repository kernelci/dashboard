from http import HTTPStatus
import json
from unittest.mock import patch
from django.test import SimpleTestCase
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.views.hardwareDetailsCommitHistoryView import (
    HardwareDetailsCommitHistoryView,
)
from rest_framework.test import APIRequestFactory
from datetime import datetime, timezone


class TestHardwareDetailsCommitHistoryView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = HardwareDetailsCommitHistoryView()
        self.url = "/hardware/1/commit-history"

    @patch(
        "kernelCI_app.views.hardwareDetailsCommitHistoryView.get_hardware_commit_history"
    )
    def test_get_hardware_details_commit_history_returns_table_when_rows_valid(
        self, mock_get_hardware_commit_history
    ):
        start_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
        mock_get_hardware_commit_history.return_value = [
            (
                "tree1",
                "repo1",
                "branch1",
                ["tag1"],
                "name1",
                "hash1",
                start_time,
            ),
        ]

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "commitHeads": [],
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, 200)
        self.assertIn("commit_history_table", response.data)
        self.assertIn("tree1-repo1-branch1", response.data["commit_history_table"])
        self.assertEqual(
            response.data["commit_history_table"]["tree1-repo1-branch1"][0][
                "git_commit_hash"
            ],
            "hash1",
        )
        self.assertEqual(
            response.data["commit_history_table"]["tree1-repo1-branch1"][0][
                "start_time"
            ],
            start_time,
        )

    @patch(
        "kernelCI_app.views.hardwareDetailsCommitHistoryView.get_hardware_commit_history"
    )
    def test_get_hardware_details_commit_history_success(
        self, mock_get_hardware_commit_history
    ):
        mock_get_hardware_commit_history.return_value = [
            ("tree1", "repo1", "branch1", "commit1", "tag1", "name1", "hash1", "time1"),
        ]

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "commitHeads": [],
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"commit_history_table": {}})

    def test_get_hardware_details_commit_history_ok_with_error(self):
        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "commitHeads": [],
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.data, {"error": ClientStrings.HARDWARE_COMMIT_HISTORY_NOT_FOUND}
        )

    def test_get_hardware_details_commit_history_invalid_json_body(self):
        request = self.factory.post(
            self.url,
            data="invalid json",
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.data, {"error": ClientStrings.INVALID_JSON_BODY})

    def test_get_hardware_details_commit_history_invalid_timestamp(self):
        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": "invalid",
                    "endTimestampInSeconds": "invalid",
                    "commitHeads": [],
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.data, {"error": ClientStrings.INVALID_TIMESTAMP})

    def test_get_hardware_details_commit_history_invalid_body_schema(self):
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
        self.assertIn("commitHeads", response.data)

    @patch.object(HardwareDetailsCommitHistoryView, "_sanitize_checkouts")
    @patch(
        "kernelCI_app.views.hardwareDetailsCommitHistoryView.get_hardware_commit_history"
    )
    def test_get_hardware_details_commit_history_response_validation_error(
        self,
        mock_get_hardware_commit_history,
        mock_sanitize_checkouts,
    ):
        mock_get_hardware_commit_history.return_value = [
            ("tree1", "repo1", "branch1", ["tag1"], "name1", "hash1", "time1"),
        ]
        mock_sanitize_checkouts.return_value = {"bad-key": [{"start_time": "invalid"}]}

        request = self.factory.post(
            self.url,
            data=json.dumps(
                {
                    "origin": "maestro",
                    "startTimestampInSeconds": 1737487800,
                    "endTimestampInSeconds": 1737574200,
                    "commitHeads": [],
                }
            ),
            content_type="application/json",
        )
        response = self.view.post(request, hardware_id="1")

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, str)
