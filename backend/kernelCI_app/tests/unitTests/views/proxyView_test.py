from http import HTTPStatus
from unittest.mock import patch

from django.test.testcases import SimpleTestCase
from rest_framework.test import APIRequestFactory

import requests
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.views.proxyView import TIMEOUT_TIME_IN_SECONDS, ProxyView

MOCK_ALLOWED_DOMAINS = ["*.example.com", "exact.org"]
MOCK_ALLOWED_S3_PATHS = ["/allowed-bucket/"]


class TestProxyView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ProxyView()
        self.url = "/proxy/"

    @patch("kernelCI_app.views.proxyView.ALLOWED_DOMAINS", MOCK_ALLOWED_DOMAINS)
    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_success(self, mock_requests_get):
        mock_requests_get.return_value.status_code = HTTPStatus.OK
        mock_requests_get.return_value.content = b"file content"
        mock_requests_get.return_value.headers = {
            "Content-Type": "text/plain",
            "Content-Length": "12",
            "Content-Disposition": "attachment; filename=file.txt",
        }

        request = self.factory.get(
            self.url, {"url": "https://files.example.com/file.txt"}
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"file content")
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertEqual(response["Content-Length"], "12")
        self.assertEqual(
            response["Content-Disposition"], "attachment; filename=file.txt"
        )
        mock_requests_get.assert_called_once_with(
            "https://files.example.com/file.txt",
            stream=True,
            timeout=TIMEOUT_TIME_IN_SECONDS,
        )

    @patch("kernelCI_app.views.proxyView.ALLOWED_DOMAINS", MOCK_ALLOWED_DOMAINS)
    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_default_content_type(self, mock_requests_get):
        mock_requests_get.return_value.status_code = HTTPStatus.OK
        mock_requests_get.return_value.content = b"content"
        mock_requests_get.return_value.headers = {}

        request = self.factory.get(
            self.url, {"url": "https://files.example.com/file.txt"}
        )
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

    def test_get_proxy_invalid_scheme(self):
        request = self.factory.get(self.url, {"url": "file:///etc/passwd"})
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.data, {"error": ClientStrings.PROXY_INVALID_URL})

    @patch("kernelCI_app.views.proxyView.ALLOWED_DOMAINS", MOCK_ALLOWED_DOMAINS)
    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_external_error(self, mock_requests_get):
        mock_requests_get.return_value.status_code = HTTPStatus.NOT_FOUND
        mock_requests_get.return_value.reason = "Not Found"

        request = self.factory.get(
            self.url, {"url": "https://files.example.com/file.txt"}
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn(ClientStrings.PROXY_FETCH_FAILED, response.data["error"])

    @patch("kernelCI_app.views.proxyView.ALLOWED_DOMAINS", MOCK_ALLOWED_DOMAINS)
    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_request_exception(self, mock_requests_get):
        mock_requests_get.side_effect = requests.RequestException("Connection error")

        request = self.factory.get(
            self.url, {"url": "https://files.example.com/file.txt"}
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, {"error": ClientStrings.PROXY_ERROR_FETCH})

    @patch("kernelCI_app.views.proxyView.ALLOWED_DOMAINS", MOCK_ALLOWED_DOMAINS)
    def test_get_proxy_forbidden_domain(self):
        request = self.factory.get(self.url, {"url": "https://evil.com/file.txt"})
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.data, {"error": ClientStrings.PROXY_FORBIDDEN_DOMAIN})

    @patch("kernelCI_app.views.proxyView.ALLOWED_DOMAINS", MOCK_ALLOWED_DOMAINS)
    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_wildcard_domain_match(self, mock_requests_get):
        mock_requests_get.return_value.status_code = HTTPStatus.OK
        mock_requests_get.return_value.content = b"content"
        mock_requests_get.return_value.headers = {}

        request = self.factory.get(
            self.url, {"url": "https://any-sub.example.com/file.txt"}
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)

    @patch("kernelCI_app.views.proxyView.ALLOWED_DOMAINS", MOCK_ALLOWED_DOMAINS)
    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_exact_domain_match(self, mock_requests_get):
        mock_requests_get.return_value.status_code = HTTPStatus.OK
        mock_requests_get.return_value.content = b"content"
        mock_requests_get.return_value.headers = {}

        request = self.factory.get(self.url, {"url": "https://exact.org/file.txt"})
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)

    @patch("kernelCI_app.views.proxyView.ALLOWED_S3_PATHS", MOCK_ALLOWED_S3_PATHS)
    @patch("kernelCI_app.views.proxyView.ALLOWED_DOMAINS", ["s3.amazonaws.com"])
    @patch("kernelCI_app.views.proxyView.requests.get")
    def test_get_proxy_s3_allowed_bucket(self, mock_requests_get):
        mock_requests_get.return_value.status_code = HTTPStatus.OK
        mock_requests_get.return_value.content = b"log content"
        mock_requests_get.return_value.headers = {}

        request = self.factory.get(
            self.url,
            {"url": "https://s3.amazonaws.com/allowed-bucket/file.log"},
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, 200)

    @patch("kernelCI_app.views.proxyView.ALLOWED_S3_PATHS", MOCK_ALLOWED_S3_PATHS)
    @patch("kernelCI_app.views.proxyView.ALLOWED_DOMAINS", ["s3.amazonaws.com"])
    def test_get_proxy_s3_forbidden_bucket(self):
        request = self.factory.get(
            self.url,
            {"url": "https://s3.amazonaws.com/other-bucket/file.log"},
        )
        response = self.view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.data, {"error": ClientStrings.PROXY_FORBIDDEN_DOMAIN})
