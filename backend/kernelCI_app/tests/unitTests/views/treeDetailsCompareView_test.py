from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.views.treeDetailsCompareView import (
    TreeDetailsBootsCompare,
    TreeDetailsTestsCompare,
)


class TestTreeDetailsCompareView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.boots_view = TreeDetailsBootsCompare()
        self.tests_view = TreeDetailsTestsCompare()
        self.commit_a = "aaa111"
        self.commit_b = "bbb222"

    def _row(self, commit_hash: str, status: str, path: str = "boot") -> dict:
        return {
            "git_commit_hash": commit_hash,
            "path": path,
            "status": status,
            "config_name": "defconfig",
            "platform": "qemu",
            "environment_compatible": ["qemu"],
            "compiler_arch": ["gcc", "x86_64"],
            "lab": "lab-a",
            "origin": "maestro",
            "known_issues": [],
        }

    @patch("kernelCI_app.views.treeDetailsCompareView.get_tree_compare_data")
    def test_boots_compare_returns_diff(self, mock_query):
        mock_query.return_value = [
            self._row(self.commit_a, "PASS"),
            self._row(self.commit_b, "FAIL"),
        ]
        request = self.factory.get(
            "/api/tree/mainline/master/boots/compare",
            {
                "origin": "maestro",
                "commit_a": self.commit_a,
                "commit_b": self.commit_b,
            },
        )
        response = self.boots_view.get(
            request, tree_name="mainline", git_branch="master"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status_a"], "PASS")
        self.assertEqual(response.data[0]["status_b"], "FAIL")
        mock_query.assert_called_once()
        self.assertEqual(mock_query.call_args.kwargs["data_type"], "boots")

    @patch("kernelCI_app.views.treeDetailsCompareView.get_tree_compare_data")
    def test_tests_compare_uses_tests_data_type(self, mock_query):
        mock_query.return_value = [
            self._row(self.commit_a, "PASS", path="ltp.smoke"),
            self._row(self.commit_b, "SKIP", path="ltp.smoke"),
        ]
        request = self.factory.get(
            "/api/tree/mainline/master/tests/compare",
            {
                "origin": "maestro",
                "commit_a": self.commit_a,
                "commit_b": self.commit_b,
            },
        )
        response = self.tests_view.get(
            request, tree_name="mainline", git_branch="master"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["status_a"], "PASS")
        self.assertEqual(response.data[0]["status_b"], "INCONCLUSIVE")
        self.assertEqual(mock_query.call_args.kwargs["data_type"], "tests")

    @patch("kernelCI_app.views.treeDetailsCompareView.get_tree_compare_data")
    def test_missing_commit_params_returns_error(self, mock_query):
        request = self.factory.get(
            "/api/tree/mainline/master/boots/compare",
            {"origin": "maestro"},
        )
        response = self.boots_view.get(
            request, tree_name="mainline", git_branch="master"
        )
        self.assertEqual(response.status_code, 400)
        mock_query.assert_not_called()
