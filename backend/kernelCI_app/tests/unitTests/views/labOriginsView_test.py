from unittest.mock import patch

from django.test.testcases import SimpleTestCase
from pydantic import ValidationError
from rest_framework.test import APIRequestFactory

from kernelCI_app.views.labOriginsView import LabOriginsView


class TestLabOriginsView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = LabOriginsView()
        self.url = "/labs/origins"

    @patch("kernelCI_app.views.labOriginsView.get_lab_origins")
    def test_get_lab_origins_success(self, mock_get_lab_origins):
        mock_get_lab_origins.return_value = ["redhat", "maestro"]
        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"origins": ["maestro", "redhat"]})
        mock_get_lab_origins.assert_called_once()

    @patch("kernelCI_app.views.labOriginsView.get_lab_origins")
    def test_get_lab_origins_empty_does_not_fail(self, mock_get_lab_origins):
        mock_get_lab_origins.return_value = []
        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"origins": []})

    @patch("kernelCI_app.views.labOriginsView.OriginsQueryParameters.model_validate")
    def test_get_lab_origins_query_validation_error(self, mock_validate):
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

    @patch("kernelCI_app.views.labOriginsView.get_lab_origins")
    @patch("kernelCI_app.views.labOriginsView.LabOriginsResponse")
    def test_get_lab_origins_response_validation_error(
        self, mock_response_class, mock_get_lab_origins
    ):
        mock_get_lab_origins.return_value = ["maestro"]
        mock_error = ValidationError.from_exception_data(
            "test_error",
            [
                {
                    "type": "string_type",
                    "loc": ("origins",),
                    "input": None,
                }
            ],
        )
        mock_response_class.side_effect = mock_error

        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, 500)
        self.assertIsNotNone(response.data)
