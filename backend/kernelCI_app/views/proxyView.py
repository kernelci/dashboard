from urllib.parse import urlparse
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema

# TIMEOUT to avoid people sending very large files through the proxy
TIMEOUT_TIME_IN_SECONDS = 45


class ProxyView(APIView):
    @extend_schema(
        description="Proxy endpoint to fetch from external sources and handle CORS issues",
        responses={200: bytes},
    )
    def get(self, request):
        url = request.GET.get("url")
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return Response(
                {"error": "Invalid URL"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            response = requests.get(url, stream=True, timeout=TIMEOUT_TIME_IN_SECONDS)

            if response.status_code != 200:
                return Response(
                    {"error": f"Failed to fetch resource: {response.reason}"},
                    status=response.status_code,
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
            return Response(
                {"error": "Error fetching the resource"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
