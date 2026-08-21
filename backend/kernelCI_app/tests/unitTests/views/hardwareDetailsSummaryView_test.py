import json
from http import HTTPStatus
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.views.hardwareDetailsSummaryView import HardwareDetailsSummary

SUMMARY_ROW = {
    "status": "PASS",
    "count": 1,
    "incidents_count": 0,
    "known_issues": [],
    "environment_compatible": ["test_hardware"],
    "config_name": "defconfig",
    "origin": "maestro",
    "lab": "lab1",
    "platform": "plat",
    "is_build": True,
    "is_test": False,
    "is_boot": False,
    "compiler_arch": ["gcc", "x86_64"],
    "tree_name": "mainline",
    "git_repository_url": "https://git.kernel.org",
    "git_repository_branch": "master",
    "git_commit_name": "v6.0",
    "git_commit_hash": "abc123",
    "git_commit_tags": ["v6.0"],
}

BODY = {
    "origin": "maestro",
    "startTimestampInSeconds": 1737487800,
    "endTimestampInSeconds": 1737574200,
    "selectedCommits": {},
}

QUERY_PATCH = (
    "kernelCI_app.views.hardwareDetailsSummaryView.get_hardware_details_summary"
)
HEADS_PATCH = (
    "kernelCI_app.views.hardwareDetailsSummaryView.get_hardware_trees_head_commits"
)


class TestHardwareDetailsSummarySkipTwinQuery(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.hardware_id = "test_hardware"
        self.heads = [("0", "abc123"), ("1", "def456")]

    def _post(self, body):
        request = self.factory.post(
            "/hardware/test_hardware/summary",
            data=json.dumps(body),
            content_type="application/json",
        )
        return HardwareDetailsSummary().post(request, hardware_id=self.hardware_id)

    def _body(self, **overrides):
        body = dict(BODY)
        body.update(overrides)
        return body

    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_python_filter_reuses_summary_query(self, mock_heads, mock_query):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        response = self._post(self._body(filter={"filter_boot.status": "FAIL"}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_query.assert_called_once()

    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_all_head_selected_commits_reuses_summary_query(
        self, mock_heads, mock_query
    ):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        response = self._post(self._body(selectedCommits={"0": "head", "1": "head"}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_query.assert_called_once()

    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_selected_commits_equal_to_heads_reuses_summary_query(
        self, mock_heads, mock_query
    ):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        response = self._post(
            self._body(selectedCommits={"0": "abc123", "1": "def456"})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_query.assert_called_once()

    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_extra_selected_commit_keys_still_reuse_summary_query(
        self, mock_heads, mock_query
    ):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        response = self._post(
            self._body(selectedCommits={"0": "head", "1": "head", "99": "ignored"})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_query.assert_called_once()

    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_non_head_commit_runs_second_query(self, mock_heads, mock_query):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        response = self._post(
            self._body(selectedCommits={"0": "deadbeef", "1": "head"})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(mock_query.call_count, 2)

    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_partial_tree_selection_runs_second_query(self, mock_heads, mock_query):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        response = self._post(self._body(selectedCommits={"0": "head"}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(mock_query.call_count, 2)

    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_duration_filter_runs_second_query(self, mock_heads, mock_query):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        response = self._post(
            self._body(filter={"filter_boot.duration_[lte]": ["100"]})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(mock_query.call_count, 2)
