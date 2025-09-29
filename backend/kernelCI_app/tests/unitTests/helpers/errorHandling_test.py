from http import HTTPStatus
from rest_framework.response import Response
from kernelCI_app.helpers.errorHandling import create_api_error_response


class TestCreateApiErrorResponse:
    def test_create_api_error_response_with_default_status(self):
        """Test create_api_error_response with default status code."""
        error_message = "Test error message"
        result = create_api_error_response(error_message=error_message)

        assert isinstance(result, Response)
        assert result.data == {"error": error_message}
        assert result.status_code == HTTPStatus.BAD_REQUEST.value

    def test_create_api_error_response_with_custom_status(self):
        """Test create_api_error_response with custom status code."""
        error_message = "Not found error"
        result = create_api_error_response(
            error_message=error_message, status_code=HTTPStatus.NOT_FOUND
        )

        assert isinstance(result, Response)
        assert result.data == {"error": error_message}
        assert result.status_code == HTTPStatus.NOT_FOUND.value
