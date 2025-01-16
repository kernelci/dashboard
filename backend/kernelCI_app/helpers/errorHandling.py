from django.http import JsonResponse
from http import HTTPStatus


class ExceptionWithJsonResponse(Exception):
    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.json_response = JsonResponse({"error": message}, status=status_code)

    def getJsonResponse(self):
        return self.json_response


# deprecated, should use APIView and return a Response from rest_framework.response instead
def create_error_response(
    error_message: str, status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
) -> JsonResponse:
    return JsonResponse({"error": error_message}, status=status_code.value)
