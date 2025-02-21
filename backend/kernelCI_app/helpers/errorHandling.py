import typing_extensions
from django.http import JsonResponse
from http import HTTPStatus
from rest_framework.response import Response


@typing_extensions.deprecated(
    "The `create_error_response` method is deprecated; use `create_api_error_response` "
    "and use the rest_framework.response type instead.",
    category=None,
)
def create_error_response(
    error_message: str, status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
) -> JsonResponse:
    return JsonResponse({"error": error_message}, status=status_code.value)


def create_api_error_response(
    *, error_message: str, status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
) -> Response:
    return Response({"error": error_message}, status=status_code.value)
