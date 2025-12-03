from unittest.mock import patch

from django.test.testcases import SimpleTestCase
from pydantic import ValidationError
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.views.originsView import (
    TEST_ORIGINS,
    OriginsView,
    separate_origin_records,
)


class TestSeparateOrigin:
    def test_separate_origin_no_records(self):
        result = separate_origin_records(records=[])

        assert len(result) == 0

    def test_separate_origin_with_valid_records(self):
        data = [
            {"origin": "origin1", "table": "checkouts"},
        ]
        result = separate_origin_records(records=data)

        assert result == {"origin1"}

    def test_separate_origin_no_origin(self):
        data = [
            {"table": "checkouts"},
        ]
        result = separate_origin_records(records=data)

        assert len(result) == 0

    @patch("kernelCI_app.views.originsView.log_message")
    def test_separate_origin_no_table(self, mock_log_message):
        data = [
            {"origin": "origin1"},
        ]
        result = separate_origin_records(records=data)

        assert len(result) == 0
        mock_log_message.assert_called_once()


class TestOriginsView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = OriginsView()
        self.url = "/origins"

    @patch("kernelCI_app.views.originsView.get_origins")
    def test_get_origins_success(self, mock_get_origins):
        mock_get_origins.return_value = [
            {"origin": "origin1", "table": "checkouts"},
            {"origin": "origin2", "table": "checkouts"},
        ]
        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "checkout_origins": ["origin1", "origin2"],
                "test_origins": TEST_ORIGINS,
            },
        )

    @patch("kernelCI_app.views.originsView.get_origins")
    def test_get_origins_not_found(self, mock_get_origins):
        mock_get_origins.return_value = []
        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": ClientStrings.NO_ORIGIN_FOUND})

    @patch("kernelCI_app.views.originsView.OriginsQueryParameters.model_validate")
    def test_get_origins_query_validation_error(self, mock_validate):
        mock_error = ValidationError.from_exception_data(
            "test_error",
            [
                {
                    "type": "int_parsing",
                    "loc": ("interval_in_days",),
                    "input": "invalid",
                }
            ],
        )
        mock_validate.side_effect = mock_error

        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, 500)
        self.assertIsNotNone(response.data)

    @patch("kernelCI_app.views.originsView.get_origins")
    @patch("kernelCI_app.views.originsView.OriginsResponse")
    def test_get_origins_response_validation_error(
        self, mock_response_class, mock_get_origins
    ):
        mock_get_origins.return_value = [
            {"origin": "origin1", "table": "checkouts"},
        ]

        mock_error = ValidationError.from_exception_data(
            "test_error",
            [
                {
                    "type": "string_type",
                    "loc": ("checkout_origins",),
                    "input": None,
                }
            ],
        )
        mock_response_class.side_effect = mock_error

        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, 500)
        self.assertIsNotNone(response.data)
