from django.http import JsonResponse
from enum import Enum


class StatusCodes(Enum):
    BAD_REQUEST = 400

class ExceptionWithJsonResponse(Exception):
    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.json_response = JsonResponse({"error": message}, status=status_code)

    def getJsonResponse(self):
        return self.json_response


def create_error_response(error_message: str, status_code: StatusCodes = StatusCodes.BAD_REQUEST) -> JsonResponse:
    return JsonResponse({"error": error_message}, status=status_code.value)
