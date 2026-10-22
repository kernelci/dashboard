from http import HTTPStatus
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.views.labDetailsView import LabDetailsAttentionView, LabDetailsView


class TestLabDetailsView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = "/labs/lava-demo/"

    @patch("kernelCI_app.views.labDetailsView.get_lab_test_rows")
    @patch("kernelCI_app.views.labDetailsView.get_lab_build_rows")
    def test_get_empty_lab_details(self, mock_builds, mock_tests):
        mock_builds.return_value = []
        mock_tests.return_value = []
        request = self.factory.get(
            self.url,
            {"origin": "maestro", "interval_in_days": "7"},
        )
        response = LabDetailsView().get(request, lab_name="lava-demo")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["lab_name"], "lava-demo")
        self.assertEqual(response.data["trees"], [])

    def test_invalid_interval_returns_bad_request(self):
        request = self.factory.get(
            self.url,
            {"origin": "maestro", "interval_in_days": "-1"},
        )
        response = LabDetailsView().get(request, lab_name="lava-demo")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class TestLabDetailsAttentionView(SimpleTestCase):
    @patch("kernelCI_app.views.labDetailsView.get_lab_attention_items")
    def test_attention_items(self, mock_attention):
        mock_attention.return_value = []
        request = APIRequestFactory().get(
            "/labs/lava-demo/lab-attention/",
            {"origin": "maestro", "interval_in_days": "7"},
        )
        response = LabDetailsAttentionView().get(request, lab_name="lava-demo")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"items": []})
