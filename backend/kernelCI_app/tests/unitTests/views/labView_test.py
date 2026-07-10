from http import HTTPStatus
from unittest.mock import patch

from django.test.testcases import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.views.labView import LabView


class TestLabView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = LabView()
        self.url = "/labs"

    @patch("kernelCI_app.views.labView.get_lab_listing_data")
    def test_get_lab_listing_success(self, mock_get_lab_listing_data):
        mock_get_lab_listing_data.return_value = [
            ("lab-collabora", *range(9)),
        ]

        query_params = {
            "interval_in_days": "7",
            "origin": "maestro",
        }

        request = self.factory.get(self.url, query_params)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_get_lab_listing_data.assert_called_once_with(
            origin="maestro",
            interval_in_days=7,
        )
        self.assertEqual(
            response.data,
            {
                "labs": [
                    {
                        "lab_name": "lab-collabora",
                        "build_status_summary": {
                            "PASS": 0,
                            "FAIL": 1,
                            "INCONCLUSIVE": 2,
                        },
                        "boot_status_summary": {
                            "PASS": 3,
                            "FAIL": 4,
                            "INCONCLUSIVE": 5,
                        },
                        "test_status_summary": {
                            "PASS": 6,
                            "FAIL": 7,
                            "INCONCLUSIVE": 8,
                        },
                    }
                ]
            },
        )

    def test_get_lab_listing_invalid_query_params_returns_bad_request(self):
        request = self.factory.get(
            self.url,
            {"origin": "maestro", "interval_in_days": "-1"},
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("interval_in_days", response.data)

    @patch("kernelCI_app.views.labView.get_lab_listing_data")
    def test_get_lab_listing_no_labs_found_returns_ok_with_error(
        self, mock_get_lab_listing_data
    ):
        mock_get_lab_listing_data.return_value = []

        query_params = {
            "interval_in_days": "7",
            "origin": "maestro",
        }

        request = self.factory.get(self.url, query_params)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"error": ClientStrings.NO_LABS_FOUND})

    @patch("kernelCI_app.views.labView.get_lab_listing_data")
    def test_get_lab_listing_sanitize_validation_error_returns_internal_server_error(
        self, mock_get_lab_listing_data
    ):
        mock_get_lab_listing_data.return_value = [
            (None, *range(9)),
        ]

        query_params = {
            "interval_in_days": "7",
            "origin": "maestro",
        }

        request = self.factory.get(self.url, query_params)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn("lab_name", response.data["error"])
