from unittest import TestCase
from unittest.mock import MagicMock, patch

from kernelCI_app.management.commands.treeproof import Command


class TestDefineTreeName(TestCase):
    def setUp(self):
        self.command = Command()

    def test_https_org_repo(self):
        url = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
        self.assertEqual(self.command._define_tree_name(url), "torvalds-linux")

    def test_trailing_slash(self):
        url = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/"
        self.assertEqual(self.command._define_tree_name(url), "torvalds-linux")

    def test_single_path_segment(self):
        url = "https://example.com/linux.git"
        self.assertEqual(self.command._define_tree_name(url), "linux")

    def test_no_git_suffix(self):
        url = "https://android.googlesource.com/kernel/common"
        self.assertEqual(self.command._define_tree_name(url), "kernel-common")

    def test_ssh_url(self):
        url = "ssh://git@github.com/org/repo.git"
        self.assertEqual(self.command._define_tree_name(url), "org-repo")

    def test_ssh_url_with_port(self):
        url = "ssh://git@github.com:22/org/repo.git"
        self.assertEqual(self.command._define_tree_name(url), "org-repo")

    def test_repo_substring_of_org(self):
        url = "https://example.com/linux/linux.git"
        self.assertEqual(self.command._define_tree_name(url), "linux")

    def test_unmatched_returns_none(self):
        for url in (
            "",
            "   ",
            "https://example.com/",
            "https://example.com",
            "linux.git",
            "git@github.com:org/repo.git",
            "not a url at all!!!",
            None,
        ):
            self.assertIsNone(self.command._define_tree_name(url), msg=repr(url))


class TestGetTreesProofsSkip(TestCase):
    @patch("kernelCI_app.management.commands.treeproof.Checkouts.objects")
    def test_skips_unparseable_url(self, mock_objects):
        records = [
            {"tree_name": None, "git_repository_url": "https://example.com/"},
            {
                "tree_name": None,
                "git_repository_url": (
                    "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
                ),
            },
        ]
        query = MagicMock()
        query.distinct.return_value = query
        query.filter.return_value = query
        query.exclude.return_value = records
        mock_objects.values.return_value = query

        command = Command()
        with self.assertLogs(
            "kernelCI_app.management.commands.treeproof", level="WARNING"
        ) as logs:
            command._get_trees_proofs()

        self.assertEqual(
            command.non_maestro_trees,
            {
                "torvalds-linux": (
                    "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
                )
            },
        )
        self.assertTrue(any("https://example.com/" in msg for msg in logs.output))
