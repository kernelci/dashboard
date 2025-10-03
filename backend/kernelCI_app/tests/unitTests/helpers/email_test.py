import pytest
from unittest.mock import patch, MagicMock
from kernelCI_app.helpers.email import (
    smtp_setup_connection,
    smtp_send_email,
)


class TestSmtpSetupConnection:
    @patch("kernelCI_app.helpers.email.get_connection")
    def test_smtp_setup_connection(self, mock_get_connection):
        """Test smtp_setup_connection returns Django connection."""
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection

        result = smtp_setup_connection()

        assert result == mock_connection
        mock_get_connection.assert_called_once()


class TestSmtpSendEmail:
    @patch("kernelCI_app.helpers.email.EmailMessage")
    @patch("kernelCI_app.helpers.email.make_msgid")
    @patch("builtins.print")
    def test_smtp_send_email_success(
        self, mock_print, mock_make_msgid, mock_email_class
    ):
        """Test smtp_send_email with successful send."""
        mock_connection = MagicMock()
        mock_email = MagicMock()
        mock_email.send.return_value = 1
        mock_make_msgid.return_value = "<test@example.com>"
        mock_email_class.return_value = mock_email

        result = smtp_send_email(
            connection=mock_connection,
            sender_email="sender@example.com",
            to="recipient@example.com",
            subject="Test Subject",
            message_text="Test message",
            cc="cc@example.com",
            reply_to="reply@example.com",
            in_reply_to="<previous@example.com>",
        )

        assert result == "<test@example.com>"
        mock_email.send.assert_called_once()
        mock_print.assert_called_once_with(
            "Message sent successfully! Message ID: <test@example.com>"
        )

    @patch("kernelCI_app.helpers.email.EmailMessage")
    @patch("kernelCI_app.helpers.email.make_msgid")
    @patch("builtins.print")
    def test_smtp_send_email_failure(
        self, mock_print, mock_make_msgid, mock_email_class
    ):
        """Test smtp_send_email with failed send."""
        mock_connection = MagicMock()
        mock_email = MagicMock()
        mock_email.send.return_value = 0
        mock_make_msgid.return_value = "<test@example.com>"
        mock_email_class.return_value = mock_email

        result = smtp_send_email(
            connection=mock_connection,
            sender_email="sender@example.com",
            to="recipient@example.com",
            subject="Test Subject",
            message_text="Test message",
            cc=None,
            reply_to=None,
            in_reply_to=None,
        )

        assert result == "<test@example.com>"
        mock_email.send.assert_called_once()
        mock_print.assert_called_once_with("Failed to send message. Result: 0")

    @patch("kernelCI_app.helpers.email.EmailMessage")
    @patch("kernelCI_app.helpers.email.make_msgid")
    def test_smtp_send_email_with_cc_list(self, mock_make_msgid, mock_email_class):
        """Test smtp_send_email with CC list."""
        mock_connection = MagicMock()
        mock_email = MagicMock()
        mock_email.send.return_value = 1
        mock_make_msgid.return_value = "<test@example.com>"
        mock_email_class.return_value = mock_email

        smtp_send_email(
            connection=mock_connection,
            sender_email="sender@example.com",
            to="recipient@example.com",
            subject="Test Subject",
            message_text="Test message",
            cc="cc1@example.com, cc2@example.com",
            reply_to="reply@example.com",
            in_reply_to=None,
        )

        mock_email_class.assert_called_once()
        call_args = mock_email_class.call_args
        assert call_args[1]["cc"] == ["cc1@example.com", "cc2@example.com"]

    @patch("kernelCI_app.helpers.email.EmailMessage")
    @patch("kernelCI_app.helpers.email.make_msgid")
    def test_smtp_send_email_with_empty_cc(self, mock_make_msgid, mock_email_class):
        """Test smtp_send_email with empty CC."""
        mock_connection = MagicMock()
        mock_email = MagicMock()
        mock_email.send.return_value = 1
        mock_make_msgid.return_value = "<test@example.com>"
        mock_email_class.return_value = mock_email

        smtp_send_email(
            connection=mock_connection,
            sender_email="sender@example.com",
            to="recipient@example.com",
            subject="Test Subject",
            message_text="Test message",
            cc="",
            reply_to="reply@example.com",
            in_reply_to=None,
        )

        call_args = mock_email_class.call_args
        assert call_args[1]["cc"] == []

    @patch("kernelCI_app.helpers.email.EmailMessage")
    @patch("kernelCI_app.helpers.email.make_msgid")
    @patch("builtins.print")
    def test_smtp_send_email_exception(
        self, mock_print, mock_make_msgid, mock_email_class
    ):
        """Test smtp_send_email with exception."""
        mock_connection = MagicMock()
        mock_email = MagicMock()
        mock_email.send.side_effect = Exception("SMTP error")
        mock_make_msgid.return_value = "<test@example.com>"
        mock_email_class.return_value = mock_email

        with pytest.raises(Exception, match="SMTP error"):
            smtp_send_email(
                connection=mock_connection,
                sender_email="sender@example.com",
                to="recipient@example.com",
                subject="Test Subject",
                message_text="Test message",
                cc=None,
                reply_to=None,
                in_reply_to=None,
            )

        mock_print.assert_called_once_with("An error occurred: SMTP error")
