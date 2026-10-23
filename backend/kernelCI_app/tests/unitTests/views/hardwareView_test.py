from http import HTTPStatus
from unittest.mock import ANY, patch

from django.test.testcases import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.views.hardwareView import HardwareView


class TestHardwareView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = HardwareView()
        self.url = "/hardware"

    @patch("kernelCI_app.views.hardwareView.get_hardware_listing_data")
    def test_get_hardware_listing_defaults_to_maestro_builds(
        self, mock_get_hardware_listing
    ):
        mock_get_hardware_listing.return_value = [
            ("platform1", "hardware1", *range(9)),
        ]

        query_params = {
            "startTimestampInSeconds": "1741192200",
            "endTimestampInSeconds": "1741624200",
        }

        request = self.factory.get(self.url, query_params)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_get_hardware_listing.assert_called_once_with(
            checkout_origin=[DEFAULT_ORIGIN],
            build_origin=[DEFAULT_ORIGIN],
            test_origin=None,
            build_lab=None,
            test_lab=None,
            start_date=ANY,
            end_date=ANY,
            commits_list=None,
        )

    @patch("kernelCI_app.views.hardwareView.get_hardware_listing_data")
    def test_get_hardware_listing_honours_deprecated_origin(
        self, mock_get_hardware_listing
    ):
        mock_get_hardware_listing.return_value = [
            ("platform1", "hardware1", *range(9)),
        ]

        query_params = {
            "startTimestampInSeconds": "1741192200",
            "endTimestampInSeconds": "1741624200",
            "origin": "origin1",
        }

        request = self.factory.get(self.url, query_params)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_get_hardware_listing.assert_called_once_with(
            checkout_origin=["origin1"],
            build_origin=["origin1"],
            test_origin=None,
            build_lab=None,
            test_lab=None,
            start_date=ANY,
            end_date=ANY,
            commits_list=None,
        )

    @patch("kernelCI_app.views.hardwareView.get_hardware_listing_data")
    def test_get_hardware_listing_passes_commits_list(self, mock_get_hardware_listing):
        mock_get_hardware_listing.return_value = [
            ("platform1", "hardware1", *range(9)),
        ]
        h1 = "a" * 40
        h2 = "b" * 40

        request = self.factory.get(
            self.url,
            {
                "startTimestampInSeconds": "1741192200",
                "endTimestampInSeconds": "1741624200",
                "origin": "origin1",
                "commitsList": f"{h1},{h2}",
            },
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_get_hardware_listing.assert_called_once_with(
            checkout_origin=["origin1"],
            build_origin=["origin1"],
            test_origin=None,
            build_lab=None,
            test_lab=None,
            start_date=ANY,
            end_date=ANY,
            commits_list=[h1, h2],
        )

    @patch("kernelCI_app.views.hardwareView.get_hardware_listing_data")
    def test_get_hardware_listing_passes_independent_filters(
        self, mock_get_hardware_listing
    ):
        mock_get_hardware_listing.return_value = [
            ("platform1", "hardware1", *range(9)),
        ]

        request = self.factory.get(
            self.url,
            {
                "startTimestampInSeconds": "1741192200",
                "endTimestampInSeconds": "1741624200",
                "checkoutOrigin": "",
                "buildOrigin": "build-origin",
                "testOrigin": "test-origin",
                "buildLab": "build-lab",
                "testLab": "test-lab",
            },
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_get_hardware_listing.assert_called_once_with(
            checkout_origin=None,
            build_origin=["build-origin"],
            test_origin=["test-origin"],
            build_lab=["build-lab"],
            test_lab=["test-lab"],
            start_date=ANY,
            end_date=ANY,
            commits_list=None,
        )

    def test_get_hardware_listing_invalid_query_params_returns_bad_request(self):
        query_params = {"origin": "origin1"}

        request = self.factory.get(self.url, query_params)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("start_date", response.data)
        self.assertIn("end_date", response.data)

    @patch("kernelCI_app.views.hardwareView.get_hardware_listing_data")
    def test_get_hardware_listing_no_hardware_found_returns_ok_with_error(
        self, mock_get_hardware_listing
    ):
        mock_get_hardware_listing.return_value = []

        query_params = {
            "startTimestampInSeconds": "1741192200",
            "endTimestampInSeconds": "1741624200",
            "origin": "origin1",
        }

        request = self.factory.get(self.url, query_params)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"error": ClientStrings.NO_HARDWARE_FOUND})

    @patch("kernelCI_app.views.hardwareView.get_hardware_listing_data")
    def test_get_hardware_listing_from_row_validation_error_returns_internal_server_error(
        self, mock_get_hardware_listing
    ):
        mock_get_hardware_listing.return_value = [
            (None, "hardware1", *range(9)),
        ]

        query_params = {
            "startTimestampInSeconds": "1741192200",
            "endTimestampInSeconds": "1741624200",
            "origin": "origin1",
        }

        request = self.factory.get(self.url, query_params)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn("platform", response.data)
