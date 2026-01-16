from http import HTTPStatus
from unittest.mock import patch
from django.test.testcases import SimpleTestCase
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.views.hardwareView import HardwareView
from rest_framework.test import APIRequestFactory


class TestHardwareView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = HardwareView()
        self.url = "/hardware"

    @patch("kernelCI_app.views.hardwareView.get_hardware_listing_data")
    def test_get_hardware_listing_success(self, mock_get_hardware_listing_data):
        mock_get_hardware_listing_data.return_value = [
            ("platform1", "hardware1", *range(22)),
        ]

        query_params = {
            "startTimestampInSeconds": "1741192200",
            "endTimestampInSeconds": "1741624200",
            "origin": "origin1",
        }

        request = self.factory.get(self.url, query_params)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_hardware_listing_invalid_query_params_returns_bad_request(self):
        query_params = {"origin": "origin1"}

        request = self.factory.get(self.url, query_params)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("start_date", response.data)
        self.assertIn("end_date", response.data)

    @patch("kernelCI_app.views.hardwareView.get_hardware_listing_data")
    def test_get_hardware_listing_no_hardware_found_returns_ok_with_error(
        self, mock_get_hardware_listing_data
    ):
        mock_get_hardware_listing_data.return_value = []

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
    def test_get_hardware_listing_sanitize_validation_error_returns_internal_server_error(
        self, mock_get_hardware_listing_data
    ):
        mock_get_hardware_listing_data.return_value = [
            (None, "hardware1", *range(22)),
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
