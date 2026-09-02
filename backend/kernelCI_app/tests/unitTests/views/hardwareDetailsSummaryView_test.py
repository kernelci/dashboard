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

    def _assert_query_count(self, body, n):
        with patch(HEADS_PATCH) as mock_heads, patch(QUERY_PATCH) as mock_query:
            mock_heads.return_value = self.heads
            mock_query.return_value = [SUMMARY_ROW]
            response = self._post(body)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(mock_query.call_count, n)

    def test_reuses_when_sql_matches_heads(self):
        cases = {
            "default": self._body(),
            "python_filter": self._body(filter={"filter_boot.status": "FAIL"}),
            "head_tokens": self._body(selectedCommits={"0": "head", "1": "head"}),
            "head_tokens_extra_key": self._body(
                selectedCommits={"0": "head", "1": "head", "99": "ignored"}
            ),
            "raw_hashes": self._body(selectedCommits={"0": "abc123", "1": "def456"}),
        }
        for name, body in cases.items():
            with self.subTest(name):
                self._assert_query_count(body, 1)

    def test_second_query_when_sql_differs(self):
        cases = {
            "non_head": self._body(selectedCommits={"0": "deadbeef", "1": "head"}),
            "partial_trees": self._body(selectedCommits={"0": "head"}),
            "duration": self._body(filter={"filter_boot.duration_[lte]": ["100"]}),
        }
        for name, body in cases.items():
            with self.subTest(name):
                self._assert_query_count(body, 2)
