from http import HTTPStatus
from unittest.mock import ANY, patch

from django.test.testcases import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.views.hardwareView import HardwareFiltersView, HardwareView

LISTING_QUERY = "kernelCI_app.views.hardwareView.get_hardware_listing_data"
FILTERS_QUERY = "kernelCI_app.views.hardwareView.get_hardware_filters"


class TestHardwareView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = HardwareView()
        self.url = "/hardware"

    def _get(self, **query_params):
        request = self.factory.get(
            self.url,
            {
                "startTimestampInSeconds": "1741192200",
                "endTimestampInSeconds": "1741624200",
                **query_params,
            },
        )
        return self.view.get(request)

    @patch(LISTING_QUERY)
    def test_get_hardware_listing_success(self, mock_listing_data):
        mock_listing_data.return_value = [
            ("platform1", "hardware1", *range(9)),
        ]

        response = self._get(origin="origin1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_listing_data.assert_called_once_with(
            start_date=ANY,
            end_date=ANY,
            checkout_origin=None,
            build_origin=None,
            build_lab=None,
            test_origin="origin1",
            test_lab=None,
            commits_list=None,
        )

    @patch(LISTING_QUERY)
    def test_get_hardware_listing_passes_commits_list(self, mock_listing_data):
        mock_listing_data.return_value = [
            ("platform1", "hardware1", *range(9)),
        ]
        h1 = "a" * 40
        h2 = "b" * 40

        response = self._get(origin="origin1", commitsList=f"{h1},{h2}")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(mock_listing_data.call_args.kwargs["commits_list"], [h1, h2])

    @patch(LISTING_QUERY)
    def test_get_hardware_listing_passes_all_filters(self, mock_listing_data):
        mock_listing_data.return_value = [
            ("platform1", "hardware1", *range(9)),
        ]

        response = self._get(
            checkoutOrigin="checkout1",
            buildOrigin="build1",
            buildLab="buildlab1",
            testOrigin="test1",
            testLab="testlab1",
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_listing_data.assert_called_once_with(
            start_date=ANY,
            end_date=ANY,
            checkout_origin="checkout1",
            build_origin="build1",
            build_lab="buildlab1",
            test_origin="test1",
            test_lab="testlab1",
            commits_list=None,
        )

    @patch(LISTING_QUERY)
    def test_get_hardware_listing_leaves_test_origin_unset(self, mock_listing_data):
        """An absent test origin must not fall back to the default one, otherwise the
        listing could not show every origin at once."""
        mock_listing_data.return_value = [
            ("platform1", "hardware1", *range(9)),
        ]

        response = self._get(checkoutOrigin="origin2")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsNone(mock_listing_data.call_args.kwargs["test_origin"])

    @patch(LISTING_QUERY)
    def test_get_hardware_listing_test_origin_takes_precedence_over_alias(
        self, mock_listing_data
    ):
        mock_listing_data.return_value = [
            ("platform1", "hardware1", *range(9)),
        ]

        response = self._get(origin="legacy", testOrigin="origin1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(mock_listing_data.call_args.kwargs["test_origin"], "origin1")

    def test_get_hardware_listing_invalid_query_params_returns_bad_request(self):
        request = self.factory.get(self.url, {"origin": "origin1"})
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("start_date", response.data)
        self.assertIn("end_date", response.data)

    @patch(LISTING_QUERY)
    def test_get_hardware_listing_no_hardware_found_returns_ok_with_error(
        self, mock_listing_data
    ):
        mock_listing_data.return_value = []

        response = self._get(origin="origin1")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"error": ClientStrings.NO_HARDWARE_FOUND})

    @patch(LISTING_QUERY)
    def test_get_hardware_listing_sanitize_validation_error_returns_internal_server_error(
        self, mock_listing_data
    ):
        mock_listing_data.return_value = [
            (None, "hardware1", *range(9)),
        ]

        response = self._get(origin="origin1")

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn("platform", response.data)


class TestHardwareFiltersView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = HardwareFiltersView()

    def _get(self, **query_params):
        request = self.factory.get("/hardware/filters", query_params)
        return self.view.get(request)

    @patch(FILTERS_QUERY)
    def test_get_hardware_filters_returns_every_list(self, mock_filters):
        mock_filters.return_value = {
            "checkout_origins": ["broonie", "maestro"],
            "build_origins": ["maestro"],
            "build_labs": ["maestro"],
            "test_origins": ["maestro", "ti"],
            "test_labs": ["lava-collabora", "lava-kontron"],
        }

        response = self._get(
            startTimestampInSeconds="1741192200",
            endTimestampInSeconds="1741624200",
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, mock_filters.return_value)

    def test_get_hardware_filters_invalid_query_params_returns_bad_request(self):
        response = self._get()

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("start_date", response.data)
