from http import HTTPStatus
from rest_framework.response import Response


def create_api_error_response(
    *, error_message: str, status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
) -> Response:
    return Response({"error": error_message}, status=status_code.value)
