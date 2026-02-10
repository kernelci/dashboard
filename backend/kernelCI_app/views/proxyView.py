from urllib.parse import ParseResult, urlparse
import requests
from fnmatch import fnmatch
from rest_framework.views import APIView
from django.http import HttpResponse
from http import HTTPStatus
from drf_spectacular.utils import extend_schema
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.typeModels.commonOpenApiParameters import URL_QUERY_PARAM
from kernelCI_app.constants.localization import ClientStrings

# TIMEOUT to avoid people sending very large files through the proxy
TIMEOUT_TIME_IN_SECONDS = 45

ALLOWED_DOMAINS = [
    # KernelCI infrastructure
    "*.kernelci.org",
    # External CI/test infrastructure
    "syzkaller.appspot.com",
    "*.sirena.org.uk",
    "lisalogs6a28e896.blob.core.windows.net",
    "storage.tuxsuite.com",
    "s3.amazonaws.com",
    "*.linaro.org",
]

ALLOWED_S3_PATHS = [
    "/arr-cki-prod-trusted-artifacts/",
]


def is_valid_url(parsed_url: ParseResult) -> bool:
    if not parsed_url.scheme or not parsed_url.netloc:
        return False

    if parsed_url.scheme not in ["http", "https"]:
        return False

    return True


def is_allowed_domain(parsed_url: ParseResult) -> bool:
    if not any(fnmatch(parsed_url.hostname, pattern) for pattern in ALLOWED_DOMAINS):
        return False

    if parsed_url.hostname == "s3.amazonaws.com":
        if not any(
            parsed_url.path.startswith(allowed_path)
            for allowed_path in ALLOWED_S3_PATHS
        ):
            return False

    return True


class ProxyView(APIView):
    @extend_schema(
        parameters=[URL_QUERY_PARAM],
        description="Proxy endpoint to fetch from external sources and handle CORS issues",
        responses={HTTPStatus.OK: bytes},
    )
    def get(self, request):
        url = request.GET.get("url")
        if not url:
            return create_api_error_response(
                error_message=ClientStrings.PROXY_INVALID_URL
            )

        parsed_url = urlparse(url)

        if not is_valid_url(parsed_url):
            return create_api_error_response(
                error_message=ClientStrings.PROXY_INVALID_URL
            )

        if not is_allowed_domain(parsed_url):
            return create_api_error_response(
                error_message=ClientStrings.PROXY_FORBIDDEN_DOMAIN,
                status_code=HTTPStatus.FORBIDDEN,
            )

        try:
            response = requests.get(url, stream=True, timeout=TIMEOUT_TIME_IN_SECONDS)

            if response.status_code != HTTPStatus.OK:
                return create_api_error_response(
                    error_message=(
                        f"{ClientStrings.PROXY_FETCH_FAILED} {response.reason}"
                    ),
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
                error_message=ClientStrings.PROXY_ERROR_FETCH,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
