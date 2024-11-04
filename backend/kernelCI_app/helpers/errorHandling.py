from django.http import JsonResponse


class ExceptionWithJsonResponse(Exception):
    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.json_response = JsonResponse({"error": message}, status=status_code)

    def getJsonResponse(self):
        return self.json_response
