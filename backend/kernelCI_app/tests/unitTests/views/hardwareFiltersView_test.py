from http import HTTPStatus
from unittest.mock import ANY, patch

from django.test.testcases import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.views.hardwareFiltersView import HardwareFiltersView

WINDOW = {
    "startTimestampInSeconds": "1741192200",
    "endTimestampInSeconds": "1741624200",
}


class TestHardwareFiltersView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = HardwareFiltersView()
        self.url = "/hardware/filters/"

    @patch("kernelCI_app.views.hardwareFiltersView.get_hardware_filters")
    def test_get_passes_the_requested_window(self, mock_get_hardware_filters):
        mock_get_hardware_filters.return_value = {
            "checkout_origins": [],
            "build_origins": [],
            "test_origins": [],
            "build_labs": [],
            "test_labs": [],
        }

        response = self.view.get(self.factory.get(self.url, WINDOW))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_get_hardware_filters.assert_called_once_with(start_date=ANY, end_date=ANY)

    def test_get_hardware_filters_without_window_returns_bad_request(self):
        response = self.view.get(self.factory.get(self.url))

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
