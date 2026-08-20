import json
from http import HTTPStatus
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.views.hardwareDetailsSummaryView import (
    HardwareDetailsCommonView,
    HardwareDetailsFiltersView,
    HardwareDetailsSummary,
    HardwareDetailsSummaryDataView,
)

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
COMMON_QUERY_PATCH = (
    "kernelCI_app.views.hardwareDetailsSummaryView.get_hardware_details_common"
)
HEADS_PATCH = (
    "kernelCI_app.views.hardwareDetailsSummaryView.get_hardware_trees_head_commits"
)


class TestHardwareDetailsSplitViews(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.hardware_id = "test_hardware"

    def _post(self, view, url):
        request = self.factory.post(
            url,
            data=json.dumps(BODY),
            content_type="application/json",
        )
        return view.post(request, hardware_id=self.hardware_id)

    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_summary_data_returns_summary_only(self, mock_heads, mock_query):
        mock_heads.return_value = [("0", "abc123")]
        mock_query.return_value = [SUMMARY_ROW]
        response = self._post(
            HardwareDetailsSummaryDataView(),
            "/hardware/test_hardware/summary-data",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("summary", response.data)
        self.assertNotIn("common", response.data)
        self.assertNotIn("filters", response.data)
        mock_query.assert_called_once()

    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_filters_returns_filters_only(self, mock_heads, mock_query):
        mock_heads.return_value = [("0", "abc123")]
        mock_query.return_value = [SUMMARY_ROW]
        response = self._post(
            HardwareDetailsFiltersView(),
            "/hardware/test_hardware/filters",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("filters", response.data)
        self.assertNotIn("summary", response.data)
        self.assertNotIn("common", response.data)
        mock_query.assert_called_once()

    @patch(COMMON_QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_common_returns_common_only(self, mock_heads, mock_query):
        mock_heads.return_value = [("0", "abc123")]
        mock_query.return_value = [SUMMARY_ROW]
        response = self._post(
            HardwareDetailsCommonView(),
            "/hardware/test_hardware/common",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("common", response.data)
        trees = response.data["common"]["trees"]
        self.assertEqual(trees[0]["head_git_commit_hash"], "abc123")
        self.assertNotIn("summary", response.data)
        self.assertNotIn("filters", response.data)
        mock_query.assert_called_once()

    @patch(HEADS_PATCH)
    def test_no_commits(self, mock_heads):
        mock_heads.return_value = []
        response = self._post(
            HardwareDetailsFiltersView(),
            "/hardware/test_hardware/filters",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["error"], ClientStrings.HARDWARE_NO_COMMITS)

    @patch(COMMON_QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_not_found(self, mock_heads, mock_query):
        mock_heads.return_value = [("0", "abc123")]
        mock_query.return_value = []
        response = self._post(
            HardwareDetailsCommonView(),
            "/hardware/test_hardware/common",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["error"], ClientStrings.HARDWARE_NOT_FOUND)


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

    @patch(COMMON_QUERY_PATCH)
    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_python_filter_reuses_summary_query(
        self, mock_heads, mock_query, mock_common
    ):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        mock_common.return_value = [SUMMARY_ROW]
        response = self._post(self._body(filter={"filter_boot.status": "FAIL"}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_query.assert_called_once()

    @patch(COMMON_QUERY_PATCH)
    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_all_head_selected_commits_reuses_summary_query(
        self, mock_heads, mock_query, mock_common
    ):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        mock_common.return_value = [SUMMARY_ROW]
        response = self._post(self._body(selectedCommits={"0": "head", "1": "head"}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_query.assert_called_once()

    @patch(COMMON_QUERY_PATCH)
    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_non_head_commit_runs_second_query(
        self, mock_heads, mock_query, mock_common
    ):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        mock_common.return_value = [SUMMARY_ROW]
        response = self._post(
            self._body(selectedCommits={"0": "deadbeef", "1": "head"})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(mock_query.call_count, 2)

    @patch(COMMON_QUERY_PATCH)
    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_partial_tree_selection_runs_second_query(
        self, mock_heads, mock_query, mock_common
    ):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        mock_common.return_value = [SUMMARY_ROW]
        response = self._post(self._body(selectedCommits={"0": "head"}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(mock_query.call_count, 2)

    @patch(COMMON_QUERY_PATCH)
    @patch(QUERY_PATCH)
    @patch(HEADS_PATCH)
    def test_duration_filter_runs_second_query(
        self, mock_heads, mock_query, mock_common
    ):
        mock_heads.return_value = self.heads
        mock_query.return_value = [SUMMARY_ROW]
        mock_common.return_value = [SUMMARY_ROW]
        response = self._post(
            self._body(filter={"filter_boot.duration_[lte]": ["100"]})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(mock_query.call_count, 2)
