from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.helpers.treeCompare import (
    build_compare_response,
    change_counts_from_row,
    process_build_rows,
    process_rollup_rows,
)
from kernelCI_app.typeModels.treeCompare import CompareChangeCounts
from kernelCI_app.views.treeCompareView import TreeCompareView

HASH_A = "a" * 40
HASH_B = "b" * 40

ROLLUP_BOOT_ROW = {
    "git_commit_hash": HASH_A,
    "path_group": "boot",
    "build_architecture": "arm64",
    "hardware_key": "qemu-arm64",
    "test_platform": "qemu-arm64",
    "is_boot": True,
    "pass_tests": 10,
    "fail_tests": 2,
    "skip_tests": 0,
    "error_tests": 1,
    "miss_tests": 0,
    "done_tests": 0,
    "null_tests": 0,
    "total_tests": 13,
}

ROLLUP_TEST_ROW_A = {
    **ROLLUP_BOOT_ROW,
    "git_commit_hash": HASH_A,
    "path_group": "kselftest",
    "build_architecture": "x86_64",
    "is_boot": False,
    "pass_tests": 20,
    "fail_tests": 5,
    "error_tests": 0,
    "total_tests": 25,
}

ROLLUP_TEST_ROW_B = {
    **ROLLUP_TEST_ROW_A,
    "git_commit_hash": HASH_B,
    "pass_tests": 18,
    "fail_tests": 7,
    "total_tests": 25,
}

BUILD_ROW_A = {
    "git_commit_hash": HASH_A,
    "git_repository_url": "https://git.kernel.org/linux.git",
    "architecture": "arm64",
    "status": "PASS",
    "count": 3,
}

BUILD_ROW_B = {
    **BUILD_ROW_A,
    "git_commit_hash": HASH_B,
    "status": "FAIL",
    "count": 2,
}


class TestTreeCompareHelper(SimpleTestCase):
    def test_process_rollup_rows_aggregates_summary(self):
        accumulators = process_rollup_rows(
            rows=[ROLLUP_BOOT_ROW, ROLLUP_TEST_ROW_A],
            commit_hashes=[HASH_A],
        )

        acc = accumulators[HASH_A]
        self.assertEqual(acc.boots.pass_count, 10)
        self.assertEqual(acc.boots.fail_count, 2)
        self.assertEqual(acc.boots.inconclusive, 1)
        self.assertEqual(acc.tests.pass_count, 20)
        self.assertEqual(acc.tests.fail_count, 5)

    def test_process_build_rows_aggregates_status_counts(self):
        accumulators = process_build_rows(
            rows=[BUILD_ROW_A, BUILD_ROW_B],
            commit_hashes=[HASH_A, HASH_B],
        )

        self.assertEqual(accumulators[HASH_A].builds.pass_count, 3)
        self.assertEqual(accumulators[HASH_B].builds.fail_count, 2)

    def test_build_compare_response_computes_deltas(self):
        rollup_data = process_rollup_rows(
            rows=[ROLLUP_TEST_ROW_A, ROLLUP_TEST_ROW_B],
            commit_hashes=[HASH_A, HASH_B],
        )
        build_data = process_build_rows(
            rows=[BUILD_ROW_A, BUILD_ROW_B],
            commit_hashes=[HASH_A, HASH_B],
        )

        accumulators = {
            HASH_A: rollup_data[HASH_A],
            HASH_B: rollup_data[HASH_B],
        }
        accumulators[HASH_A].builds = build_data[HASH_A].builds
        accumulators[HASH_B].builds = build_data[HASH_B].builds

        response = build_compare_response(
            hash_a=HASH_A,
            hash_b=HASH_B,
            tree_name="linux",
            branch="master",
            git_url="https://git.kernel.org/linux.git",
            accumulators=accumulators,
            changes={
                "builds": CompareChangeCounts(regression=1),
                "boots": CompareChangeCounts(),
                "tests": CompareChangeCounts(new_failure=2, still_failing=3),
            },
        )

        payload = response.model_dump(by_alias=True)
        self.assertNotIn("groups", payload)
        self.assertEqual(payload["summary"]["tests"]["delta"]["pass"], -2)
        self.assertEqual(payload["summary"]["tests"]["delta"]["fail"], 2)
        self.assertEqual(payload["summary"]["builds"]["delta"]["pass"], -3)
        self.assertEqual(payload["summary"]["builds"]["delta"]["fail"], 2)
        self.assertEqual(payload["summary"]["builds"]["changes"]["regression"], 1)
        self.assertEqual(payload["summary"]["tests"]["changes"]["newFailure"], 2)
        self.assertEqual(payload["summary"]["tests"]["changes"]["stillFailing"], 3)

    def test_change_counts_from_row(self):
        counts = change_counts_from_row(
            {
                "regression": 4,
                "fixed": 1,
                "new_failure": 2,
                "still_failing": 7,
                "new_pass": 9,
                "appeared": 3,
                "disappeared": 8,
            }
        )
        self.assertEqual(counts.regression, 4)
        self.assertEqual(counts.new_failure, 2)
        self.assertEqual(counts.appeared, 3)
        self.assertEqual(counts.disappeared, 8)
        self.assertEqual(counts.model_dump(by_alias=True)["stillFailing"], 7)


class TestTreeCompareView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = TreeCompareView.as_view()
        self.url = "/api/tree/linux/master/compare"

    @patch("kernelCI_app.views.treeCompareView.get_tree_compare_tests_change_counts")
    @patch("kernelCI_app.views.treeCompareView.get_tree_compare_boots_change_counts")
    @patch("kernelCI_app.views.treeCompareView.get_tree_compare_builds_change_counts")
    @patch("kernelCI_app.views.treeCompareView.get_tree_compare_rollup")
    @patch("kernelCI_app.views.treeCompareView.get_tree_compare_builds")
    def test_get_returns_compare_payload(
        self,
        mock_builds,
        mock_rollup,
        mock_build_changes,
        mock_boot_changes,
        mock_test_changes,
    ):
        mock_builds.return_value = [BUILD_ROW_A, BUILD_ROW_B]
        mock_rollup.return_value = [
            ROLLUP_BOOT_ROW,
            ROLLUP_TEST_ROW_A,
            ROLLUP_TEST_ROW_B,
        ]
        mock_build_changes.return_value = {
            "regression": 1,
            "fixed": 0,
            "new_failure": 0,
            "still_failing": 0,
            "new_pass": 0,
        }
        mock_boot_changes.return_value = {
            "regression": 0,
            "fixed": 0,
            "new_failure": 0,
            "still_failing": 0,
            "new_pass": 0,
        }
        mock_test_changes.return_value = {
            "regression": 2,
            "fixed": 1,
            "new_failure": 3,
            "still_failing": 4,
            "new_pass": 5,
        }

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
        self.assertEqual(response.data["treeName"], "linux")
        self.assertEqual(response.data["branch"], "master")
        self.assertIn("summary", response.data)
        self.assertNotIn("groups", response.data)
        self.assertEqual(response.data["summary"]["builds"]["changes"]["regression"], 1)
        self.assertEqual(
            response.data["summary"]["tests"]["changes"]["stillFailing"], 4
        )
        mock_builds.assert_called_once()
        mock_rollup.assert_called_once()
        mock_build_changes.assert_called_once()
        mock_boot_changes.assert_called_once()
        mock_test_changes.assert_called_once()
        self.assertNotIn("git_url_param", mock_builds.call_args.kwargs)

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

    @patch("kernelCI_app.views.treeCompareView.get_tree_compare_tests_change_counts")
    @patch("kernelCI_app.views.treeCompareView.get_tree_compare_boots_change_counts")
    @patch("kernelCI_app.views.treeCompareView.get_tree_compare_builds_change_counts")
    @patch("kernelCI_app.views.treeCompareView.get_tree_compare_rollup")
    @patch("kernelCI_app.views.treeCompareView.get_tree_compare_builds")
    def test_missing_checkout_returns_zero_counts(
        self,
        mock_builds,
        mock_rollup,
        mock_build_changes,
        mock_boot_changes,
        mock_test_changes,
    ):
        mock_builds.return_value = []
        mock_rollup.return_value = []
        empty = {
            "regression": 0,
            "fixed": 0,
            "new_failure": 0,
            "still_failing": 0,
            "new_pass": 0,
        }
        mock_build_changes.return_value = empty
        mock_boot_changes.return_value = empty
        mock_test_changes.return_value = empty

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
        self.assertEqual(response.data["summary"]["builds"]["sideA"]["pass"], 0)
        self.assertEqual(response.data["summary"]["tests"]["sideB"]["fail"], 0)
        self.assertEqual(response.data["summary"]["builds"]["changes"]["regression"], 0)
