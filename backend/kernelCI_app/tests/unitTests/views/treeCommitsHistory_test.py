from datetime import datetime, timezone
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.views.treeCommitsHistory import (
    TreeCommitsHistory,
    TreeCommitsHistoryDirect,
    TreeCommitsHistoryList,
)


class TestTreeCommitsHistory(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = TreeCommitsHistory()
        self.direct_view = TreeCommitsHistoryDirect()
        self.commit_hash = "1f44358e5057873ced21617aca6443b8b9e9c191"
        self.url = f"/api/tree/{self.commit_hash}/commits"

    @patch("kernelCI_app.views.treeCommitsHistory.get_tree_commit_history")
    def test_builds_with_hardware_filter_returns_non_empty_response(
        self, mock_get_tree_commit_history
    ):
        mock_get_tree_commit_history.return_value = [
            (
                self.commit_hash,
                "commit-name",
                ["v1"],
                datetime(2026, 2, 1, tzinfo=timezone.utc),
                120,
                "x86_64",
                "gcc",
                "defconfig",
                "PASS",
                "maestro",
                "build-1",
                {"platform": "acer-cp514-2h-1160g7-volteer", "lab": "lab-a"},
                "boot",
                "PASS",
                30,
                ["acer-cp514-2h-1160g7-volteer"],
                {"runtime": {"platform": "acer-cp514-2h-1160g7-volteer"}},
                "maestro",
                "lab-a",
                "test-1",
                None,
                None,
                None,
                None,
            )
        ]

        request = self.factory.get(
            self.url,
            {
                "origin": "maestro",
                "git_url": "https://chromium.googlesource.com/chromiumos/third_party/kernel.git",
                "git_branch": "chromeos-5.4",
                "start_timestamp_in_seconds": "1769779800",
                "end_timestamp_in_seconds": "1771507800",
                "types": "builds",
                "builds_related_to_filtered_tests_only": "true",
                "filter_test.hardware": "acer-cp514-2h-1160g7-volteer",
            },
        )

        response = self.view.get(request, commit_hash=self.commit_hash)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["git_commit_hash"], self.commit_hash)
        self.assertEqual(response.data[0]["builds"]["PASS"], 1)
        self.assertEqual(sum(response.data[0]["boots"].values()), 0)
        self.assertEqual(sum(response.data[0]["tests"].values()), 0)

        mock_get_tree_commit_history.assert_called_once_with(
            commit_hash=self.commit_hash,
            origin="maestro",
            git_url="https://chromium.googlesource.com/chromiumos/third_party/kernel.git",
            git_branch="chromeos-5.4",
            tree_name=None,
            include_types=["builds", "boots", "tests"],
        )

    @patch("kernelCI_app.views.treeCommitsHistory.get_tree_commit_history")
    def test_builds_default_scope_does_not_expand_include_types(
        self, mock_get_tree_commit_history
    ):
        mock_get_tree_commit_history.return_value = [
            (
                self.commit_hash,
                "commit-name",
                ["v1"],
                datetime(2026, 2, 1, tzinfo=timezone.utc),
                120,
                "x86_64",
                "gcc",
                "defconfig",
                "PASS",
                "maestro",
                "build-1",
                {"platform": "acer-cp514-2h-1160g7-volteer", "lab": "lab-a"},
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            )
        ]

        request = self.factory.get(
            self.url,
            {
                "origin": "maestro",
                "git_url": "https://chromium.googlesource.com/chromiumos/third_party/kernel.git",
                "git_branch": "chromeos-5.4",
                "types": "builds",
            },
        )

        response = self.view.get(request, commit_hash=self.commit_hash)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["builds"]["PASS"], 1)

        mock_get_tree_commit_history.assert_called_once_with(
            commit_hash=self.commit_hash,
            origin="maestro",
            git_url="https://chromium.googlesource.com/chromiumos/third_party/kernel.git",
            git_branch="chromeos-5.4",
            tree_name=None,
            include_types=["builds"],
        )

    @patch("kernelCI_app.views.treeCommitsHistory.get_tree_commit_history")
    def test_builds_relation_scope_counts_only_builds_linked_to_filtered_tests(
        self, mock_get_tree_commit_history
    ):
        target_hardware = "acer-cp514-2h-1160g7-volteer"

        mock_get_tree_commit_history.return_value = [
            (
                self.commit_hash,
                "commit-name",
                ["v1"],
                datetime(2026, 2, 1, tzinfo=timezone.utc),
                120,
                "x86_64",
                "gcc",
                "defconfig",
                "PASS",
                "maestro",
                "build-unrelated",
                {"platform": target_hardware, "lab": "lab-a"},
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
            (
                self.commit_hash,
                "commit-name",
                ["v1"],
                datetime(2026, 2, 1, tzinfo=timezone.utc),
                180,
                "x86_64",
                "gcc",
                "defconfig",
                "PASS",
                "maestro",
                "build-related",
                {"platform": "some-other-platform", "lab": "lab-a"},
                "boot",
                "PASS",
                30,
                [target_hardware],
                {"runtime": {"platform": target_hardware}},
                "maestro",
                "lab-a",
                "test-related",
                None,
                None,
                None,
                None,
            ),
        ]

        request = self.factory.get(
            self.url,
            {
                "origin": "maestro",
                "git_url": "https://chromium.googlesource.com/chromiumos/third_party/kernel.git",
                "git_branch": "chromeos-5.4",
                "types": "builds",
                "builds_related_to_filtered_tests_only": "true",
                "filter_test.hardware": target_hardware,
            },
        )

        response = self.view.get(request, commit_hash=self.commit_hash)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["builds"]["PASS"], 1)
        self.assertEqual(sum(response.data[0]["boots"].values()), 0)
        self.assertEqual(sum(response.data[0]["tests"].values()), 0)

    @patch("kernelCI_app.views.treeCommitsHistory.get_tree_commit_history")
    def test_direct_tree_details_builds_with_hardware_filter_is_not_empty(
        self, mock_get_tree_commit_history
    ):
        commit_hash = "6bd9ed02871f22beb0e50690b0c3caf457104f7c"
        hardware = "fsl,imx8mp-evk"
        direct_url = f"/api/tree/mainline/master/{commit_hash}/commits"

        mock_get_tree_commit_history.return_value = [
            (
                commit_hash,
                "commit-name",
                ["v1"],
                datetime(2026, 2, 1, tzinfo=timezone.utc),
                120,
                "arm64",
                "gcc",
                "defconfig",
                "PASS",
                "maestro",
                "build-1",
                {"platform": hardware, "lab": "lab-a"},
                None,
                None,
                None,
                None,
                {"platform": "unknown"},
                None,
                "lab-a",
                None,
                None,
                None,
                None,
                None,
            )
        ]

        request = self.factory.get(
            direct_url,
            {
                "origin": "maestro",
                "git_url": "",
                "git_branch": "master",
                "types": "builds",
                "filter_test.hardware": hardware,
            },
        )

        response = self.direct_view.get(
            request,
            commit_hash=commit_hash,
            tree_name="mainline",
            git_branch="master",
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]["builds"]["PASS"], 1)


class TestTreeCommitsHistoryList(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = TreeCommitsHistoryList()
        self.url = "/api/tree/commits"

    @patch(
        "kernelCI_app.views.treeCommitsHistory.get_tree_commit_history_hashes_aggregated"
    )
    def test_tree_commits_history_list_success(self, mock_get_aggregated):
        mock_get_aggregated.return_value = [
            {
                "count": 5,
                "git_commit_hash": "abc123",
                "git_commit_name": "v6.1",
                "git_commit_tags": ["v1"],
                "start_time": datetime(2026, 2, 1, tzinfo=timezone.utc),
                "origin": "maestro",
                "status": "PASS",
                "compiler_arch": ["gcc", "x86_64"],
                "config_name": "defconfig",
                "lab": "lab-a",
                "known_issues": ["issue-1,1"],
                "is_build": True,
                "is_boot": False,
                "is_test": False,
            }
        ]

        request = self.factory.get(
            self.url,
            {
                "origin": "maestro",
                "commit_hashes": "abc123,def456",
            },
        )

        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["git_commit_hash"], "abc123")
        self.assertEqual(response.data[0]["builds"]["PASS"], 5)
        mock_get_aggregated.assert_called_once()

    @patch(
        "kernelCI_app.views.treeCommitsHistory.get_tree_commit_history_hashes_aggregated"
    )
    def test_tree_commits_history_list_with_types_filter(self, mock_aggregated):
        mock_aggregated.return_value = [
            {
                "count": 10,
                "git_commit_hash": "abc123",
                "git_commit_name": "v6.1",
                "git_commit_tags": None,
                "start_time": datetime(2026, 2, 1, tzinfo=timezone.utc),
                "origin": "maestro",
                "status": "FAIL",
                "compiler_arch": ["gcc", "x86_64"],
                "config_name": "defconfig",
                "lab": "lab-a",
                "known_issues": None,
                "is_build": False,
                "is_boot": False,
                "is_test": True,
            }
        ]

        request = self.factory.get(
            self.url,
            {
                "origin": "maestro",
                "commit_hashes": "abc123",
                "types": "tests",
            },
        )

        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        mock_aggregated.assert_called_once()

    @patch(
        "kernelCI_app.views.treeCommitsHistory.get_tree_commit_history_hashes_aggregated"
    )
    def test_tree_commits_history_list_with_no_commit_hashes_returns_error(
        self, mock_aggregated
    ):
        request = self.factory.get(
            self.url,
            {
                "origin": "maestro",
            },
        )

        response = self.view.get(request)

        self.assertEqual(response.status_code, 400)
        mock_aggregated.assert_not_called()

    @patch(
        "kernelCI_app.views.treeCommitsHistory.get_tree_commit_history_hashes_aggregated"
    )
    def test_tree_commits_history_list_empty_results(self, mock_aggregated):
        mock_aggregated.return_value = []

        request = self.factory.get(
            self.url,
            {
                "origin": "maestro",
                "commit_hashes": "nonexistent_hash",
            },
        )

        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {"error": ClientStrings.TREE_COMMITS_HISTORY_NOT_FOUND},
        )
        mock_aggregated.assert_called_once()
