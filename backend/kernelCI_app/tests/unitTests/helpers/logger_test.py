from unittest.mock import patch, MagicMock
from django.http import HttpRequest
from kernelCI_app.constants.general import PRODUCTION_HOST, STAGING_HOST
from kernelCI_app.helpers.logger import log_message, create_endpoint_notification


class TestLogMessage:
    @patch("builtins.print")
    def test_log_message_basic(self, mock_print):
        """Test log_message prints the message."""
        message = "Test log message"
        log_message(message)
        mock_print.assert_called_once_with(message)

    @patch("builtins.print")
    def test_log_message_empty_string(self, mock_print):
        """Test log_message with empty string."""
        message = ""
        log_message(message)
        mock_print.assert_called_once_with("")

    @patch("builtins.print")
    def test_log_message_none(self, mock_print):
        """Test log_message with None (should not happen but testing robustness)."""
        message = None
        log_message(message)
        mock_print.assert_called_once_with(None)


class TestCreateEndpointNotification:
    @patch("kernelCI_app.helpers.logger.get_running_instance")
    def test_create_endpoint_notification_production(self, mock_get_running_instance):
        """Test create_endpoint_notification with production instance."""
        mock_get_running_instance.return_value = "production"

        request = MagicMock(spec=HttpRequest)
        request.get_full_path.return_value = "/api/test"
        request.body = b'{"test": "data"}'

        message = "Test notification"
        result = create_endpoint_notification(message=message, request=request)

        assert message in result
        assert PRODUCTION_HOST in result

    @patch("kernelCI_app.helpers.logger.get_running_instance")
    def test_create_endpoint_notification_staging(self, mock_get_running_instance):
        """Test create_endpoint_notification with staging instance."""
        mock_get_running_instance.return_value = "staging"

        request = MagicMock(spec=HttpRequest)
        request.get_full_path.return_value = "/api/test"
        request.body = b'{"test": "data"}'

        message = "Test notification"
        result = create_endpoint_notification(message=message, request=request)

        assert message in result
        assert STAGING_HOST in result

    @patch("kernelCI_app.helpers.logger.get_running_instance")
    def test_create_endpoint_notification_none_instance(
        self, mock_get_running_instance
    ):
        """Test create_endpoint_notification with None instance."""
        mock_get_running_instance.return_value = None

        request = MagicMock(spec=HttpRequest)
        request.get_full_path.return_value = "/api/test"
        request.build_absolute_uri.return_value = "https://localhost:8000/api/test"
        request.body = b'{"test": "data"}'

        message = "Test notification"
        result = create_endpoint_notification(message=message, request=request)

        assert message in result
        assert request.build_absolute_uri() in result
