from http import HTTPStatus
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.queries.hardwareRegistryFilters import (
    HardwareRegistryFilter,
    get_hardware_registry_filter_options,
    normalize_csv,
    registry_filter_predicate,
)
from kernelCI_app.tests.unitTests.queries.conftest import setup_mock_cursor
from kernelCI_app.views.hardwareRegistryFiltersView import HardwareRegistryFiltersView


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
    def test_options_read_the_registry_for_the_listed_platforms(self, mock_connection):
        cursor = setup_mock_cursor(mock_connection)
        cursor.fetchone.return_value = (["arm64"], [], [], [], [], [], ["sbc"])

        options = get_hardware_registry_filter_options(["qemu", "am62", "qemu"])

        query, params = cursor.execute.call_args[0]
        self.assertIn("plat.id = ANY(%(platforms)s)", query)
        self.assertEqual(params, {"platforms": ["qemu", "am62", "qemu"]})
        self.assertEqual(options["architecture"], ["arm64"])
        self.assertEqual(options["board_type"], ["sbc"])
        self.assertEqual(options["platform"], ["am62", "qemu"])

    def test_normalize_csv_drops_blanks(self):
        self.assertEqual(normalize_csv(" arm64, ,arm "), ("arm64", "arm"))
        self.assertEqual(normalize_csv(None), ())
        self.assertEqual(normalize_csv(""), ())


_EMPTY_OPTIONS = {
    "architecture": [],
    "processor": [],
    "platform_vendor": [],
    "silicon_vendor": [],
    "platform": [],
    "system_module": [],
    "form_factor": [],
    "board_type": [],
}


_VIEW = "kernelCI_app.views.hardwareRegistryFiltersView."


@patch(_VIEW + "get_hardware_registry_filter_options", return_value=_EMPTY_OPTIONS)
class TestHardwareRegistryFiltersView(SimpleTestCase):
    def get(self, params):
        return HardwareRegistryFiltersView().get(
            APIRequestFactory().get("/api/hardware/registry-filters/", params)
        )

    @patch(_VIEW + "get_hardware_listing_data")
    def test_options_come_from_the_unfiltered_listing(self, mock_listing, mock_options):
        mock_listing.return_value = [("am62", None), ("qemu", None)]

        response = self.get(
            {
                "startTimestampInSeconds": "1741192200",
                "endTimestampInSeconds": "1741624200",
                "buildOrigin": "ti",
                "testLab": "lab-a",
                "commitsList": "abc",
                "architecture": "arm64",
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        kwargs = mock_listing.call_args.kwargs
        self.assertEqual(kwargs["checkout_origin"], [DEFAULT_ORIGIN])
        self.assertEqual(kwargs["build_origin"], ["ti"])
        self.assertEqual(kwargs["test_lab"], ["lab-a"])
        self.assertEqual(kwargs["commits_list"], ["abc"])
        self.assertNotIn("registry_filter", kwargs)
        mock_options.assert_called_once_with(["am62", "qemu"])

    @patch(_VIEW + "get_hardware_listing_data_by_revision", return_value=[])
    def test_revision_options_use_the_revision_listing(
        self, mock_revision, mock_options
    ):
        response = self.get(
            {
                "tree_name": "android",
                "git_repository_url": "https://example.com/android",
                "git_repository_branch": "main",
                "git_commit_hash": "abc",
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(mock_revision.call_args.kwargs["git_commit_hash"], "abc")
        mock_options.assert_called_once_with([])

    def test_window_is_required_without_a_revision(self, mock_options):
        response = self.get({"buildOrigin": "ti"})

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        mock_options.assert_not_called()
