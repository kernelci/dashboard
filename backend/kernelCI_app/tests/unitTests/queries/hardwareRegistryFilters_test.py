from datetime import datetime
from unittest.mock import patch

from django.test import SimpleTestCase

from kernelCI_app.queries.hardwareRegistryFilters import (
    HardwareRegistryFilter,
    get_hardware_daily_listing,
    get_hardware_daily_revision_listing,
    get_hardware_registry_filter_options,
    normalize_csv,
    registry_filter_predicate,
)
from kernelCI_app.tests.unitTests.queries.conftest import setup_mock_cursor


class TestRegistryFilterPredicate(SimpleTestCase):
    def test_empty_filter_adds_no_predicate(self):
        predicate, params = registry_filter_predicate(
            HardwareRegistryFilter(), "daily.platform"
        )

        self.assertIsNone(predicate)
        self.assertEqual(params, {})

    def test_architecture_excludes_unregistered_platforms(self):
        predicate, params = registry_filter_predicate(
            HardwareRegistryFilter(architecture=("arm64", "arm")),
            "daily.platform",
        )

        self.assertIn("proc.architecture = ANY(%(architecture)s)", predicate)
        self.assertNotIn("NOT EXISTS", predicate)
        self.assertEqual(params["architecture"], ["arm64", "arm"])

    def test_platform_id_includes_unregistered_platforms(self):
        predicate, params = registry_filter_predicate(
            HardwareRegistryFilter(platform=("am62-sk", "unknown-board")),
            "daily.platform",
        )

        self.assertEqual(predicate, "daily.platform = ANY(%(platform)s)")
        self.assertNotIn("NOT EXISTS", predicate)
        self.assertEqual(params["platform"], ["am62-sk", "unknown-board"])

    def test_platform_id_with_another_field_excludes_unregistered_platforms(self):
        predicate, params = registry_filter_predicate(
            HardwareRegistryFilter(architecture=("arm64",), platform=("am62-sk",)),
            "daily.platform",
        )

        self.assertIn("proc.architecture = ANY(%(architecture)s)", predicate)
        self.assertIn("plat.id = ANY(%(platform)s)", predicate)
        self.assertNotIn("NOT EXISTS", predicate)
        self.assertEqual(params["architecture"], ["arm64"])
        self.assertEqual(params["platform"], ["am62-sk"])

    @patch("kernelCI_app.queries.hardwareRegistryFilters.connection")
    def test_daily_listing_reads_both_tables_and_applies_the_filter(
        self, mock_connection
    ):
        cursor = setup_mock_cursor(mock_connection)
        cursor.fetchall.return_value = []

        get_hardware_daily_listing(
            origin="maestro",
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 2),
            registry_filter=HardwareRegistryFilter(architecture=("arm64",)),
        )

        query, params = cursor.execute.call_args[0]
        self.assertIn("hardware_daily_builds", query)
        self.assertIn("hardware_daily_tests", query)
        self.assertIn("tested.test_origin = %(origin)s", query)
        self.assertIn("tested.checkout_id = daily.checkout_id", query)
        self.assertNotIn("build_origin", query)
        self.assertIn("daily.test_origin = %(origin)s", query)
        self.assertIn("picked.checkout_id = daily.checkout_id", query)
        self.assertIn("checkouts.start_time DESC", query)
        self.assertIn("proc.architecture = ANY(%(architecture)s)", query)
        self.assertNotIn("NOT EXISTS", query)
        self.assertEqual(params["architecture"], ["arm64"])
        self.assertEqual(params["origin"], "maestro")

        cursor.fetchone.return_value = ([], [], [], [], [], [], [], [])
        get_hardware_registry_filter_options(
            origin="maestro",
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 2),
        )
        options_query = cursor.execute.call_args[0][0]
        self.assertIn("SELECT DISTINCT platform FROM picked", options_query)
        self.assertIn("checkouts.start_time DESC", options_query)

        get_hardware_daily_listing(
            origin="maestro",
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 2),
            commits_list=["abc"],
        )
        commits_query = cursor.execute.call_args[0][0]
        self.assertNotIn("picked", commits_query)
        self.assertIn("commits_list", commits_query)

    @patch("kernelCI_app.queries.hardwareRegistryFilters.connection")
    def test_revision_listing_and_options_use_the_same_daily_checkout(
        self, mock_connection
    ):
        cursor = setup_mock_cursor(mock_connection)
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = ([], [], [], [], [], [], [], [])
        revision = {
            "origin": "maestro",
            "tree_name": "android",
            "git_repository_url": "https://example.com/android",
            "git_repository_branch": "main",
            "git_commit_hash": "abc",
        }

        get_hardware_daily_revision_listing(
            **revision,
            registry_filter=HardwareRegistryFilter(architecture=("arm64",)),
        )
        listing_query = cursor.execute.call_args[0][0]
        self.assertIn("hardware_daily_builds", listing_query)
        self.assertIn("hardware_daily_tests", listing_query)
        self.assertIn("tested.checkout_id = daily.checkout_id", listing_query)
        self.assertNotIn("build_origin", listing_query)
        self.assertIn("revision.git_commit_hash = %(git_commit_hash)s", listing_query)
        self.assertNotIn("picked", listing_query)
        self.assertNotIn("environment_misc", listing_query)

        get_hardware_registry_filter_options(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 2),
            **revision,
        )
        options_query = cursor.execute.call_args[0][0]
        self.assertIn("hardware_daily_tests", options_query)
        self.assertNotIn("hardware_daily_builds", options_query)
        self.assertNotIn("build_origin", options_query)
        self.assertIn("revision.git_commit_hash = %(git_commit_hash)s", options_query)
        self.assertNotIn("picked", options_query)
        self.assertNotIn("checkout_day", options_query)

    def test_normalize_csv_drops_blanks(self):
        self.assertEqual(normalize_csv(" arm64, ,arm "), ("arm64", "arm"))
        self.assertEqual(normalize_csv(None), ())
        self.assertEqual(normalize_csv(""), ())
