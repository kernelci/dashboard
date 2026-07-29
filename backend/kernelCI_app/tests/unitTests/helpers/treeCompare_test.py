from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.treeCompare import (
    build_compare_rows,
    collapse_side_statuses,
    group_raw_status,
    worst_status,
)


def _row(
    *,
    commit_hash: str,
    path: str = "boot",
    status: str = "PASS",
    config_name: str = "defconfig",
    platform: str = "qemu",
    compiler: str = "gcc",
    architecture: str = "x86_64",
    lab: str = "lab-a",
    origin: str = "maestro",
    environment_compatible: list[str] | None = None,
    known_issues: list[str] | None = None,
) -> dict:
    return {
        "git_commit_hash": commit_hash,
        "path": path,
        "status": status,
        "config_name": config_name,
        "platform": platform,
        "environment_compatible": environment_compatible or [platform],
        "compiler_arch": [compiler, architecture],
        "lab": lab,
        "origin": origin,
        "known_issues": known_issues or [],
    }


class TestGroupRawStatus(SimpleTestCase):
    def test_pass_fail_and_inconclusive(self):
        self.assertEqual(group_raw_status("PASS"), "PASS")
        self.assertEqual(group_raw_status("FAIL"), "FAIL")
        self.assertEqual(group_raw_status("SKIP"), "INCONCLUSIVE")
        self.assertEqual(group_raw_status("MISS"), "INCONCLUSIVE")
        self.assertEqual(group_raw_status(None), "INCONCLUSIVE")


class TestWorstStatus(SimpleTestCase):
    def test_fail_wins(self):
        self.assertEqual(worst_status("PASS", "FAIL"), "FAIL")
        self.assertEqual(worst_status("INCONCLUSIVE", "FAIL"), "FAIL")
        self.assertEqual(worst_status("FAIL", "PASS"), "FAIL")

    def test_inconclusive_over_pass(self):
        self.assertEqual(worst_status("PASS", "INCONCLUSIVE"), "INCONCLUSIVE")
        self.assertEqual(worst_status(None, "PASS"), "PASS")


class TestBuildCompareRows(SimpleTestCase):
    def test_status_flip(self):
        rows = build_compare_rows(
            {("boot", "defconfig", "qemu"): "PASS"},
            {("boot", "defconfig", "qemu"): "FAIL"},
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].status_a, "PASS")
        self.assertEqual(rows[0].status_b, "FAIL")

    def test_one_sided_null(self):
        rows = build_compare_rows(
            {("boot", "defconfig", "qemu"): "PASS"},
            {},
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].status_a, "PASS")
        self.assertIsNone(rows[0].status_b)

    def test_same_grouped_bucket_no_diff(self):
        rows = build_compare_rows(
            {("boot", "defconfig", "qemu"): "INCONCLUSIVE"},
            {("boot", "defconfig", "qemu"): "INCONCLUSIVE"},
        )
        self.assertEqual(rows, [])

    def test_full_includes_same_grouped_bucket(self):
        rows = build_compare_rows(
            {("boot", "defconfig", "qemu"): "PASS"},
            {("boot", "defconfig", "qemu"): "PASS"},
            full=True,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].status_a, "PASS")
        self.assertEqual(rows[0].status_b, "PASS")


class TestCollapseSideStatuses(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.commit_a = "aaa"
        self.commit_b = "bbb"

    def _filters(self, params: dict | None = None) -> FilterParams:
        request = self.factory.get(
            "/api/tree/mainline/master/boots/compare", params or {}
        )
        return FilterParams(request)

    def test_worst_wins_on_collision(self):
        rows = [
            _row(commit_hash=self.commit_a, status="PASS"),
            _row(commit_hash=self.commit_a, status="FAIL"),
        ]
        collapsed, _ = collapse_side_statuses(
            rows=rows,
            commit_a=self.commit_a,
            commit_b=self.commit_b,
            filters=self._filters(),
            data_type="boots",
        )
        self.assertEqual(collapsed[("boot", "defconfig", "qemu")], "FAIL")

    def test_skip_and_miss_same_bucket(self):
        rows = [
            _row(commit_hash=self.commit_a, status="SKIP"),
            _row(commit_hash=self.commit_b, status="MISS"),
        ]
        status_a, status_b = collapse_side_statuses(
            rows=rows,
            commit_a=self.commit_a,
            commit_b=self.commit_b,
            filters=self._filters(),
            data_type="boots",
        )
        self.assertEqual(build_compare_rows(status_a, status_b), [])

    def test_config_filter_applies_both_sides(self):
        rows = [
            _row(commit_hash=self.commit_a, status="PASS", config_name="defconfig"),
            _row(commit_hash=self.commit_b, status="FAIL", config_name="defconfig"),
            _row(
                commit_hash=self.commit_a,
                status="PASS",
                config_name="otherconfig",
                path="boot.other",
            ),
            _row(
                commit_hash=self.commit_b,
                status="FAIL",
                config_name="otherconfig",
                path="boot.other",
            ),
        ]
        filters = self._filters({"filter_config_name": "defconfig"})
        status_a, status_b = collapse_side_statuses(
            rows=rows,
            commit_a=self.commit_a,
            commit_b=self.commit_b,
            filters=filters,
            data_type="boots",
        )
        compare_rows = build_compare_rows(status_a, status_b)
        self.assertEqual(len(compare_rows), 1)
        self.assertEqual(compare_rows[0].config_name, "defconfig")
