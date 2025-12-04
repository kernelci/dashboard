from http import HTTPStatus
from unittest.mock import patch

from django.test.testcases import SimpleTestCase
from rest_framework.test import APIRequestFactory

import requests
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.views.proxyView import TIMEOUT_TIME_IN_SECONDS, ProxyView


class TestProxyView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ProxyView()
        self.url = "/proxy/"

    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_success(self, mock_requests_get):
        mock_requests_get.return_value.status_code = HTTPStatus.OK
        mock_requests_get.return_value.content = b"file content"
        mock_requests_get.return_value.headers = {
            "Content-Type": "text/plain",
            "Content-Length": "12",
            "Content-Disposition": "attachment; filename=file.txt",
        }

        request = self.factory.get(self.url, {"url": "https://example.com/file.txt"})
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"file content")
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertEqual(response["Content-Length"], "12")
        self.assertEqual(
            response["Content-Disposition"], "attachment; filename=file.txt"
        )
        mock_requests_get.assert_called_once_with(
            "https://example.com/file.txt", stream=True, timeout=TIMEOUT_TIME_IN_SECONDS
        )

    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_default_content_type(self, mock_requests_get):
        mock_requests_get.return_value.status_code = HTTPStatus.OK
        mock_requests_get.return_value.content = b"content"
        mock_requests_get.return_value.headers = {}

        request = self.factory.get(self.url, {"url": "https://example.com/file.txt"})
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/octet-stream")

    def test_get_proxy_invalid_url(self):
        request = self.factory.get(self.url, {"url": "example.com/file.txt"})
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.data, {"error": ClientStrings.PROXY_INVALID_URL})

    def test_get_proxy_missing_url(self):
        request = self.factory.get(self.url)
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.data, {"error": ClientStrings.PROXY_INVALID_URL})

    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_external_error(self, mock_requests_get):
        mock_requests_get.return_value.status_code = HTTPStatus.NOT_FOUND
        mock_requests_get.return_value.reason = "Not Found"

        request = self.factory.get(self.url, {"url": "https://example.com/file.txt"})
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn(ClientStrings.PROXY_FETCH_FAILED, response.data["error"])

    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_request_exception(self, mock_requests_get):
        mock_requests_get.side_effect = requests.RequestException("Connection error")

        request = self.factory.get(self.url, {"url": "https://example.com/file.txt"})
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, {"error": ClientStrings.PROXY_ERROR_FETCH})
