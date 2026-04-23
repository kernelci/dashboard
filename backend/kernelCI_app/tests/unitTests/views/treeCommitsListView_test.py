from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.views.treeCommitsListView import TreeCommitsListView


class TestTreeCommitsListView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = TreeCommitsListView()
        self.url = "/api/tree/mainline/master/commits"

    @patch("kernelCI_app.views.treeCommitsListView.get_tree_commits")
    def test_tree_commits_list_view_success(self, mock_get_commits):
        mock_get_commits.return_value = [
            {"git_commit_hash": "abc123", "start_time_end": "2025-11-10T10:00:00Z"}
        ]

        request = self.factory.get(
            self.url,
            {
                "origin": "maestro",
            },
        )

        response = self.view.get(
            request,
            tree_name="mainline",
            git_branch="master",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @patch("kernelCI_app.views.treeCommitsListView.get_tree_commits")
    def test_tree_commits_list_view_empty(self, mock_get_commits):
        mock_get_commits.return_value = []

        request = self.factory.get(
            self.url,
            {
                "origin": "maestro",
            },
        )

        response = self.view.get(
            request,
            tree_name="mainline",
            git_branch="master",
        )

        self.assertEqual(response.status_code, 200)
        assert "error" in response.data

    @patch("kernelCI_app.views.treeCommitsListView.get_tree_commits")
    def test_tree_commits_list_view_with_git_url(self, mock_get_commits):
        mock_get_commits.return_value = [
            {"git_commit_hash": "abc123", "start_time_end": "2025-11-10T10:00:00Z"}
        ]

        request = self.factory.get(
            self.url,
            {
                "origin": "maestro",
                "git_url": "https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git",
            },
        )

        response = self.view.get(
            request,
            tree_name="mainline",
            git_branch="master",
        )

        self.assertEqual(response.status_code, 200)
        mock_get_commits.assert_called_once_with(
            origin="maestro",
            tree_name="mainline",
            git_branch="master",
            git_url="https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git",
        )
