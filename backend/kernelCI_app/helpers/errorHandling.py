import typing_extensions
from django.http import JsonResponse
from http import HTTPStatus
from rest_framework.response import Response


class ExceptionWithJsonResponse(Exception):
    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def getRestResponse(self):
        return Response(data={"error": self.message}, status=self.status_code)


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
