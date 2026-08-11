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
        self.hash_a = "aaa111"
        self.hash_b = "bbb222"

    def _diff_row(
        self,
        *,
        status_a: str | None = "PASS",
        status_b: str | None = "FAIL",
        path: str = "boot",
    ) -> dict:
        return {
            "path": path,
            "config_name": "defconfig",
            "architecture": "arm64",
            "platform": "qemu",
            "status_a": status_a,
            "status_b": status_b,
        }

    @patch(
        "kernelCI_app.views.treeDetailsCompareView.get_tree_compare_boots_tests_diff"
    )
    def test_boots_compare_returns_diff(self, mock_query):
        mock_query.return_value = [self._diff_row()]
        request = self.factory.get(
            "/api/tree/mainline/master/compare/boots",
            {
                "origin": "maestro",
                "hash_a": self.hash_a,
                "hash_b": self.hash_b,
            },
        )
        response = self.boots_view.get(
            request, tree_name="mainline", git_branch="master"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status_a"], "PASS")
        self.assertEqual(response.data[0]["status_b"], "FAIL")
        self.assertEqual(response.data[0]["architecture"], "arm64")
        self.assertEqual(response.data[0]["config_name"], "defconfig")
        mock_query.assert_called_once()
        self.assertEqual(mock_query.call_args.kwargs["data_type"], "boots")

    @patch(
        "kernelCI_app.views.treeDetailsCompareView.get_tree_compare_boots_tests_diff"
    )
    def test_tests_compare_uses_tests_data_type(self, mock_query):
        mock_query.return_value = [
            self._diff_row(path="ltp.smoke", status_a="PASS", status_b="INCONCLUSIVE")
        ]
        request = self.factory.get(
            "/api/tree/mainline/master/compare/tests",
            {
                "origin": "maestro",
                "hash_a": self.hash_a,
                "hash_b": self.hash_b,
            },
        )
        response = self.tests_view.get(
            request, tree_name="mainline", git_branch="master"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["status_a"], "PASS")
        self.assertEqual(response.data[0]["status_b"], "INCONCLUSIVE")
        self.assertEqual(mock_query.call_args.kwargs["data_type"], "tests")

    @patch(
        "kernelCI_app.views.treeDetailsCompareView.get_tree_compare_boots_tests_diff"
    )
    def test_issue_filter_uses_sql_diff_path(self, mock_diff):
        mock_diff.return_value = [
            self._diff_row(path="ltp.smoke", status_a="PASS", status_b="FAIL")
        ]
        request = self.factory.get(
            "/api/tree/mainline/master/compare/tests",
            {
                "origin": "maestro",
                "hash_a": self.hash_a,
                "hash_b": self.hash_b,
                "filter_test.issue": "issue-1,1",
            },
        )
        response = self.tests_view.get(
            request, tree_name="mainline", git_branch="master"
        )
        self.assertEqual(response.status_code, 200)
        mock_diff.assert_called_once()
        self.assertIsNotNone(mock_diff.call_args.kwargs["filters"])

    @patch(
        "kernelCI_app.views.treeDetailsCompareView.get_tree_compare_boots_tests_diff"
    )
    def test_missing_hash_params_returns_error(self, mock_query):
        request = self.factory.get(
            "/api/tree/mainline/master/compare/boots",
            {"origin": "maestro"},
        )
        response = self.boots_view.get(
            request, tree_name="mainline", git_branch="master"
        )
        self.assertEqual(response.status_code, 400)
        mock_query.assert_not_called()
