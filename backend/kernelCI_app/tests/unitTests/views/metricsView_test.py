from unittest.mock import patch

from django.test.testcases import SimpleTestCase
from pydantic import ValidationError
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.tests.unitTests.commands.metrics_notifications_test import (
    make_metrics_data,
)
from kernelCI_app.typeModels.metrics import metrics_report_data_to_response
from kernelCI_app.views.metricsView import MetricsView


class TestMetricsView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = MetricsView()
        self.url = "/metrics"

    @patch("kernelCI_app.views.metricsView.get_metrics_data")
    def test_get_metrics_success(self, mock_get_metrics_data):
        mock_get_metrics_data.return_value = make_metrics_data()
        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            metrics_report_data_to_response(make_metrics_data()).model_dump(),
        )
        mock_get_metrics_data.assert_called_once_with(start_days_ago=7, end_days_ago=0)

    @patch("kernelCI_app.views.metricsView.get_metrics_data")
    def test_get_metrics_with_custom_interval(self, mock_get_metrics_data):
        mock_get_metrics_data.return_value = make_metrics_data()
        request = self.factory.get(
            self.url, {"start_days_ago": "14", "end_days_ago": "7"}
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        mock_get_metrics_data.assert_called_once_with(start_days_ago=14, end_days_ago=7)

    def test_get_metrics_invalid_interval(self):
        request = self.factory.get(
            self.url, {"start_days_ago": "7", "end_days_ago": "7"}
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data, {"error": ClientStrings.METRICS_INVALID_INTERVAL}
        )

    @patch("kernelCI_app.views.metricsView.MetricsQueryParameters.model_validate")
    def test_get_metrics_query_validation_error(self, mock_validate):
        mock_error = ValidationError.from_exception_data(
            "test_error",
            [
                {
                    "type": "int_parsing",
                    "loc": ("start_days_ago",),
                    "input": "invalid",
                }
            ],
        )
        mock_validate.side_effect = mock_error

        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, 500)
        self.assertIsNotNone(response.data)

    @patch("kernelCI_app.views.metricsView.get_metrics_data")
    def test_get_metrics_internal_error(self, mock_get_metrics_data):
        mock_get_metrics_data.side_effect = Exception("Database unavailable")
        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data, {"error": "Database unavailable"})
