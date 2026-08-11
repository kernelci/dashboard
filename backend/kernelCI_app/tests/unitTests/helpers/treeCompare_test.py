from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.treeCompare import (
    build_boot_test_compare_filter_clauses,
    build_build_compare_filter_clauses,
)


class TestBuildCompareFilterClauses(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def _filters(self, params: dict | None = None) -> FilterParams:
        request = self.factory.get(
            "/api/tree/mainline/master/compare/builds", params or {}
        )
        return FilterParams(request)

    def test_empty_filters(self):
        result = build_build_compare_filter_clauses(self._filters())
        self.assertEqual(result.pre_join, "")
        self.assertEqual(result.post_join, "")
        self.assertEqual(result.params, {})

    def test_architecture_is_pre_join(self):
        result = build_build_compare_filter_clauses(
            self._filters({"filter_architecture": "arm64"})
        )
        self.assertIn("architectures", result.params)
        self.assertIn("b.architecture", result.pre_join)
        self.assertEqual(result.post_join, "")

    def test_status_is_post_join_grouped(self):
        result = build_build_compare_filter_clauses(
            self._filters({"filter_build.status": ["FAIL", "NULL"]})
        )
        self.assertEqual(result.pre_join, "")
        self.assertIn("a.grouped_status = ANY(%(grouped_build_statuses)s)", result.post_join)
        self.assertCountEqual(
            result.params["grouped_build_statuses"],
            ["FAIL", "INCONCLUSIVE"],
        )


class TestBootTestCompareFilterClauses(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def _filters(self, params: dict | None = None) -> FilterParams:
        request = self.factory.get(
            "/api/tree/mainline/master/compare/boots", params or {}
        )
        return FilterParams(request)

    def test_path_filter_for_boots(self):
        result = build_boot_test_compare_filter_clauses(
            self._filters({"filter_boot.path": "boot.login"}),
            "boots",
        )
        self.assertIn("test_path", result.params)
        self.assertIn("t.path", result.pre_join)

    def test_boot_status_is_post_join(self):
        result = build_boot_test_compare_filter_clauses(
            self._filters({"filter_boot.status": "PASS"}),
            "boots",
        )
        self.assertEqual(result.pre_join, "")
        self.assertIn("grouped_test_statuses", result.params)
        self.assertIn("a.grouped_status", result.post_join)
