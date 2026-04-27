from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.tests.unitTests.helpers.fixtures.tree_details_data import create_row
from kernelCI_app.views.treeDetailsSummaryView import TreeDetailsSummary

COMMIT_HASH = "abc123def456rollupfallback"

BASE_BUILD_ROW: dict[str, object] = {
    "build_id": "build_fallback_001",
    "build_origin": "maestro",
    "build_comment": None,
    "build_start_time": None,
    "build_duration": None,
    "build_architecture": "x86_64",
    "build_command": None,
    "build_compiler": "gcc-12",
    "build_config_name": "defconfig",
    "build_config_url": None,
    "build_log_url": None,
    "build_status": "PASS",
    "build_misc": None,
    "checkout_id": "checkout_fallback_001",
    "checkout_git_repository_url": "https://git.kernel.org",
    "checkout_git_repository_branch": "for-kernelci",
    "checkout_git_commit_tags": [],
    "checkout_origin": "maestro",
    "incident_id": None,
    "incident_test_id": None,
    "incident_present": None,
    "issue_id": None,
    "issue_version": None,
    "issue_comment": None,
    "issue_report_url": None,
}

BASE_ROLLUP_ROW: dict[str, object] = {
    "origin": "maestro",
    "tree_name": "mainline",
    "git_repository_branch": "for-kernelci",
    "git_repository_url": "https://git.kernel.org",
    "git_commit_hash": COMMIT_HASH,
    "path_group": "test",
    "build_config_name": "defconfig",
    "build_architecture": "x86_64",
    "build_compiler": "gcc-12",
    "hardware_key": "qemu",
    "test_platform": "qemu",
    "test_lab": "lab-a",
    "test_origin": "maestro",
    "issue_id": None,
    "issue_version": None,
    "issue_uncategorized": False,
    "is_boot": False,
    "pass_tests": 1,
    "fail_tests": 0,
    "skip_tests": 0,
    "error_tests": 0,
    "miss_tests": 0,
    "done_tests": 0,
    "null_tests": 0,
    "total_tests": 1,
    "issue_comment": None,
    "issue_report_url": None,
}

# Legacy row representing a boot test (PASS, no issue)
LEGACY_BOOT_ROW = create_row(
    test_id="legacy_boot_001",
    test_path="boot.test",
    test_status="PASS",
    incident_test_id="legacy_boot_001",
    issue_id=None,
    issue_version=None,
)

# Legacy row representing a non-boot test (FAIL, no linked issue → unknown issue)
LEGACY_TEST_ROW = create_row(
    test_id="legacy_test_001",
    test_path="test.something",
    test_status="FAIL",
    incident_test_id="legacy_test_001",
    issue_id=None,
    issue_version=None,
)


class TestTreeDetailsSummaryRollupFallback(SimpleTestCase):
    """Tests for the rollup-empty fallback path in TreeDetailsSummary."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = TreeDetailsSummary()
        self.url = f"/api/tree/{COMMIT_HASH}/summary"
        self.base_query = {
            "origin": "maestro",
            "git_url": "https://git.kernel.org",
            "git_branch": "for-kernelci",
        }

    def _make_request(self, query_overrides: dict | None = None):
        query = dict(self.base_query)
        if query_overrides:
            query.update(query_overrides)
        return self.factory.get(self.url, query)

    @patch("kernelCI_app.views.treeDetailsSummaryView.out")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_data")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_builds")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_rollup")
    def test_fallback_to_legacy_when_rollup_empty(
        self,
        mock_get_rollup,
        mock_get_builds,
        mock_get_legacy_data,
        mock_out,
    ):
        """When rollup is empty the endpoint falls back to legacy data and returns
        non-empty boot/test summaries."""
        mock_get_rollup.return_value = []
        mock_get_builds.return_value = [BASE_BUILD_ROW]
        mock_get_legacy_data.return_value = [LEGACY_BOOT_ROW, LEGACY_TEST_ROW]

        response = self.view.get(self._make_request(), commit_hash=COMMIT_HASH)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.data)

        # Fallback was triggered and logged
        mock_out.assert_called_once()

        # Boot summary is populated from legacy rows
        boot_status = response.data["summary"]["boots"]["status"]
        self.assertGreater(sum(boot_status.values()), 0)

        # Test summary is populated from legacy rows
        test_status = response.data["summary"]["tests"]["status"]
        self.assertGreater(sum(test_status.values()), 0)

        # Build summary is still correct (from _sanitize_builds_rows, not legacy)
        build_status = response.data["summary"]["builds"]["status"]
        self.assertGreater(sum(build_status.values()), 0)

    @patch("kernelCI_app.views.treeDetailsSummaryView.out")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_data")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_builds")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_rollup")
    def test_build_filter_flags_not_contaminated_by_legacy_test_rows(
        self,
        mock_get_rollup,
        mock_get_builds,
        mock_get_legacy_data,
        mock_out,
    ):
        """Build filter metadata must not be altered by test-incident rows processed
        in the legacy fallback path (fixes double-processing of build filter flags)."""
        # Build PASSES → has_unknown_issue for builds must stay False
        mock_get_rollup.return_value = []
        mock_get_builds.return_value = [BASE_BUILD_ROW]
        # A test row that has a FAIL status with incident_test_id set (test incident,
        # not a build incident). Without the fix this would incorrectly set the build
        # has_unknown_issue flag.
        mock_get_legacy_data.return_value = [LEGACY_TEST_ROW]

        response = self.view.get(self._make_request(), commit_hash=COMMIT_HASH)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.data)

        # The build filter has_unknown_issue should be False: the build passed, and
        # the test-incident rows must not bleed into build filter metadata.
        builds_filter = response.data["filters"]["builds"]
        self.assertFalse(builds_filter["has_unknown_issue"])

    @patch("kernelCI_app.views.treeDetailsSummaryView.out")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_data")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_builds")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_rollup")
    def test_no_legacy_query_when_both_empty(
        self,
        mock_get_rollup,
        mock_get_builds,
        mock_get_legacy_data,
        mock_out,
    ):
        """When both builds and rollup are empty the guard clause returns a no-results
        error without attempting the legacy query."""
        mock_get_rollup.return_value = []
        mock_get_builds.return_value = []

        response = self.view.get(self._make_request(), commit_hash=COMMIT_HASH)

        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.data)

        mock_get_legacy_data.assert_not_called()
        mock_out.assert_not_called()

    @patch("kernelCI_app.views.treeDetailsSummaryView.out")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_data")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_builds")
    @patch("kernelCI_app.views.treeDetailsSummaryView.get_tree_details_rollup")
    def test_path_filter_forces_legacy_even_with_rollup_rows(
        self,
        mock_get_rollup,
        mock_get_builds,
        mock_get_legacy_data,
        mock_out,
    ):
        """Path filters must use legacy test rows because rollup only has path_group."""
        mock_get_rollup.return_value = [BASE_ROLLUP_ROW]
        mock_get_builds.return_value = [BASE_BUILD_ROW]
        mock_get_legacy_data.return_value = [LEGACY_TEST_ROW]

        response = self.view.get(
            self._make_request({"filter_test.path": "test.something"}),
            commit_hash=COMMIT_HASH,
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.data)
        mock_get_legacy_data.assert_called_once()
        mock_out.assert_called_once()

        # Value comes from legacy row (FAIL), not from rollup row (PASS).
        test_status = response.data["summary"]["tests"]["status"]
        self.assertEqual(test_status.get("FAIL"), 1)
        self.assertEqual(test_status.get("PASS"), 0)
