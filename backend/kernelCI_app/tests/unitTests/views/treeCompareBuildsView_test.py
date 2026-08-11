from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.helpers.treeCompare import build_build_compare_filter_clauses
from kernelCI_app.views.treeCompareBuildsView import TreeCompareBuildsView

HASH_A = "a" * 40
HASH_B = "b" * 40

BUILD_DIFF_ROW = {
    "config_name": "defconfig",
    "architecture": "arm64",
    "compiler": "gcc-12",
    "status_a": "PASS",
    "status_b": "FAIL",
}


class TestBuildBuildCompareFilterClauses(SimpleTestCase):
    def test_empty_filters_add_no_clauses(self):
        result = build_build_compare_filter_clauses(None)
        self.assertEqual(result.pre_join, "")
        self.assertEqual(result.post_join, "")
        self.assertEqual(result.params, {})

    def test_build_status_post_join_and_config_pre_join(self):
        filters = MagicMock()
        filters.filterBuildStatus = {"FAIL", "NULL"}
        filters.filterBuildDurationMin = None
        filters.filterBuildDurationMax = None
        filters.filter_build_origin = set()
        filters.filterConfigs = {"defconfig"}
        filters.filterArchitecture = set()
        filters.filterCompiler = set()
        filters.filter_labs = set()
        filters.filterHardware = set()
        filters.filterIssues = {"boot": set(), "build": set(), "test": set()}

        result = build_build_compare_filter_clauses(filters)
        self.assertIn("= ANY(%(configs)s)", result.pre_join)
        self.assertIn(
            "a.grouped_status = ANY(%(grouped_build_statuses)s)",
            result.post_join,
        )
        self.assertNotIn("b.status", result.pre_join)
        self.assertCountEqual(
            result.params["grouped_build_statuses"],
            ["FAIL", "INCONCLUSIVE"],
        )
        self.assertEqual(result.params["configs"], ["defconfig"])


class TestTreeCompareBuildsView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = TreeCompareBuildsView.as_view()
        self.url = "/api/tree/linux/master/compare/builds"

    @patch("kernelCI_app.views.treeCompareBuildsView.get_tree_compare_builds_diff")
    def test_get_returns_builds_payload(self, mock_builds):
        mock_builds.return_value = [BUILD_DIFF_ROW]

        request = self.factory.get(
            self.url,
            {
                "hash_a": HASH_A,
                "hash_b": HASH_B,
                "origin": "maestro",
            },
        )
        response = self.view(request, tree_name="linux", git_branch="master")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [BUILD_DIFF_ROW])
        self.assertIn("config_name", response.data[0])
        self.assertIn("architecture", response.data[0])
        self.assertIn("compiler", response.data[0])
        self.assertIn("status_a", response.data[0])
        self.assertNotIn("configName", response.data[0])
        mock_builds.assert_called_once()
        self.assertEqual(mock_builds.call_args.kwargs["hash_a"], HASH_A)

    def test_missing_hashes_returns_400(self):
        request = self.factory.get(
            self.url,
            {
                "hash_a": HASH_A,
                "origin": "maestro",
            },
        )
        response = self.view(request, tree_name="linux", git_branch="master")
        self.assertEqual(response.status_code, 400)

    @patch("kernelCI_app.views.treeCompareBuildsView.get_tree_compare_builds_diff")
    def test_skip_vs_miss_same_bucket_yields_empty_diff(self, mock_builds):
        mock_builds.return_value = []

        request = self.factory.get(
            self.url,
            {
                "hash_a": HASH_A,
                "hash_b": HASH_B,
                "origin": "maestro",
            },
        )
        response = self.view(request, tree_name="linux", git_branch="master")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    @patch("kernelCI_app.views.treeCompareBuildsView.get_tree_compare_builds_diff")
    def test_one_sided_null_status(self, mock_builds):
        mock_builds.return_value = [
            {
                "config_name": "defconfig",
                "architecture": "arm64",
                "compiler": "gcc-12",
                "status_a": "PASS",
                "status_b": None,
            }
        ]

        request = self.factory.get(
            self.url,
            {
                "hash_a": HASH_A,
                "hash_b": HASH_B,
                "origin": "maestro",
            },
        )
        response = self.view(request, tree_name="linux", git_branch="master")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["status_a"], "PASS")
        self.assertIsNone(response.data[0]["status_b"])
