from urllib.parse import urlparse
import requests
from rest_framework.views import APIView
from django.http import HttpResponse
from http import HTTPStatus
from drf_spectacular.utils import extend_schema
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.typeModels.commonOpenApiParameters import URL_QUERY_PARAM

# TIMEOUT to avoid people sending very large files through the proxy
TIMEOUT_TIME_IN_SECONDS = 45


class ProxyView(APIView):
    @extend_schema(
        parameters=[URL_QUERY_PARAM],
        description="Proxy endpoint to fetch from external sources and handle CORS issues",
        responses={HTTPStatus.OK: bytes},
    )
    def get(self, request):
        url = request.GET.get("url")
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return create_api_error_response(error_message="Invalid URL")
        try:
            response = requests.get(url, stream=True, timeout=TIMEOUT_TIME_IN_SECONDS)

            if response.status_code != HTTPStatus.OK:
                return create_api_error_response(
                    error_message=f"Failed to fetch resource: {response.reason}",
                    status_code=HTTPStatus(response.status_code),
                )

            proxy_response = HttpResponse(
                content=response.content,
                content_type=response.headers.get(
                    "Content-Type", "application/octet-stream"
                ),
            )
            if "Content-Disposition" in response.headers:
                proxy_response["Content-Disposition"] = response.headers[
                    "Content-Disposition"
                ]

            if "Content-Length" in response.headers:
                proxy_response["Content-Length"] = response.headers["Content-Length"]

            return proxy_response

        except requests.RequestException:
            return create_api_error_response(
                error_message="Error fetching the resource",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
