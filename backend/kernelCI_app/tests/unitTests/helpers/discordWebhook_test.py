from unittest.mock import patch
import requests
from kernelCI_app.helpers.discordWebhook import (
    validate_notification,
    send_discord_notification,
    AVATAR_URL,
    WEBHOOK_NAME,
)


class TestValidateNotification:
    @patch("kernelCI_app.helpers.discordWebhook.log_message")
    def test_validate_notification_no_url(self, mock_log_message):
        """Test validate_notification with no URL or with empty URL."""
        result = validate_notification(url=None, content="Test content", embeds=None)

        assert result is False
        mock_log_message.assert_called_once_with(
            "DISCORD_WEBHOOK_URL environment variable is not set."
        )

    @patch("kernelCI_app.helpers.discordWebhook.log_message")
    def test_validate_notification_no_content_or_embeds(self, mock_log_message):
        """Test validate_notification with no or empty content or embeds."""
        result = validate_notification(
            url="https://discord.com/api/webhooks/test", content=None, embeds=None
        )

        assert result is False
        mock_log_message.assert_called_once_with(
            "Either content or embeds must be set in order to send notifications."
        )

    @patch("kernelCI_app.helpers.discordWebhook.log_message")
    def test_validate_notification_too_many_embeds(self, mock_log_message):
        """Test validate_notification with too many embeds."""
        embeds = [{"title": f"Embed {i}"} for i in range(11)]

        result = validate_notification(
            url="https://discord.com/api/webhooks/test", content=None, embeds=embeds
        )

        assert result is False
        mock_log_message.assert_called_once_with(
            "The embed list can contain at most 10 elements."
        )

    def test_validate_notification_valid_content(self):
        """Test validate_notification with valid content."""
        result = validate_notification(
            url="https://discord.com/api/webhooks/test",
            content="Test content",
            embeds=None,
        )

        assert result is True

    def test_validate_notification_valid_embeds(self):
        """Test validate_notification with valid embeds."""
        embeds = [{"title": "Test embed"}]

        result = validate_notification(
            url="https://discord.com/api/webhooks/test", content=None, embeds=embeds
        )

        assert result is True


class TestSendDiscordNotification:
    @patch("kernelCI_app.helpers.discordWebhook.os.getenv")
    @patch("kernelCI_app.helpers.discordWebhook.validate_notification")
    def test_send_discord_notification_invalid_notification(
        self, mock_validate, mock_getenv
    ):
        """Test send_discord_notification with invalid notification."""
        mock_getenv.return_value = "https://discord.com/api/webhooks/test"
        mock_validate.return_value = False

        send_discord_notification(content="Test content")

        mock_validate.assert_called_once_with(
            url="https://discord.com/api/webhooks/test",
            content="Test content",
            embeds=None,
        )

    @patch("kernelCI_app.helpers.discordWebhook.os.getenv")
    @patch("kernelCI_app.helpers.discordWebhook.validate_notification")
    @patch("kernelCI_app.helpers.discordWebhook.get_notification_cache")
    @patch("kernelCI_app.helpers.discordWebhook.set_notification_cache")
    @patch("kernelCI_app.helpers.discordWebhook.requests.post")
    @patch("kernelCI_app.helpers.discordWebhook.datetime")
    def test_send_discord_notification_with_content_success(
        self,
        mock_datetime,
        mock_post,
        mock_set_cache,
        mock_get_cache,
        mock_validate,
        mock_getenv,
    ):
        """Test send_discord_notification with content successfully."""
        mock_getenv.return_value = "https://discord.com/api/webhooks/test"
        mock_validate.return_value = True
        mock_get_cache.return_value = None
        mock_datetime.now.return_value.strftime.return_value = "2024-01-15 12:00:00 UTC"
        mock_post.return_value.raise_for_status.return_value = None

        send_discord_notification(content="Test content")

        mock_get_cache.assert_called_once_with(notification="Test content")
        mock_set_cache.assert_called_once_with(notification="Test content")
        mock_post.assert_called_once()

        call_args = mock_post.call_args
        assert call_args[1]["url"] == "https://discord.com/api/webhooks/test"
        data = call_args[1]["json"]
        assert data["avatar_url"] == AVATAR_URL
        assert data["username"] == WEBHOOK_NAME
        assert "Test content" in data["content"]
        assert "Accessed in:" in data["content"]

    @patch("kernelCI_app.helpers.discordWebhook.os.getenv")
    @patch("kernelCI_app.helpers.discordWebhook.validate_notification")
    @patch("kernelCI_app.helpers.discordWebhook.get_notification_cache")
    @patch("kernelCI_app.helpers.discordWebhook.log_message")
    def test_send_discord_notification_cached_message(
        self, mock_log_message, mock_get_cache, mock_validate, mock_getenv
    ):
        """Test send_discord_notification with cached message."""
        mock_getenv.return_value = "https://discord.com/api/webhooks/test"
        mock_validate.return_value = True
        mock_get_cache.return_value = "cached"

        send_discord_notification(content="Test content")

        mock_log_message.assert_called_once()
        assert "Message already sent" in mock_log_message.call_args[0][0]

    @patch("kernelCI_app.helpers.discordWebhook.os.getenv")
    @patch("kernelCI_app.helpers.discordWebhook.validate_notification")
    @patch("kernelCI_app.helpers.discordWebhook.get_notification_cache")
    @patch("kernelCI_app.helpers.discordWebhook.log_message")
    def test_send_discord_notification_cache_error(
        self, mock_log_message, mock_get_cache, mock_validate, mock_getenv
    ):
        """Test send_discord_notification with cache error."""
        mock_getenv.return_value = "https://discord.com/api/webhooks/test"
        mock_validate.return_value = True
        mock_get_cache.side_effect = Exception("Cache error")

        send_discord_notification(content="Test content")

        mock_log_message.assert_called_once()
        assert (
            "Error when getting discord notification cache"
            in mock_log_message.call_args[0][0]
        )

    @patch("kernelCI_app.helpers.discordWebhook.os.getenv")
    @patch("kernelCI_app.helpers.discordWebhook.validate_notification")
    @patch("kernelCI_app.helpers.discordWebhook.requests.post")
    def test_send_discord_notification_with_embeds(
        self, mock_post, mock_validate, mock_getenv
    ):
        """Test send_discord_notification with embeds."""
        mock_getenv.return_value = "https://discord.com/api/webhooks/test"
        mock_validate.return_value = True
        mock_post.return_value.raise_for_status.return_value = None

        embeds = [{"title": "Test embed", "description": "Test description"}]

        send_discord_notification(embeds=embeds)

        mock_post.assert_called_once()

        call_args = mock_post.call_args
        data = call_args[1]["json"]
        assert data["avatar_url"] == AVATAR_URL
        assert data["username"] == WEBHOOK_NAME
        assert data["embeds"] == embeds
        assert "content" not in data

    @patch("kernelCI_app.helpers.discordWebhook.os.getenv")
    @patch("kernelCI_app.helpers.discordWebhook.validate_notification")
    @patch("kernelCI_app.helpers.discordWebhook.get_notification_cache")
    @patch("kernelCI_app.helpers.discordWebhook.set_notification_cache")
    @patch("kernelCI_app.helpers.discordWebhook.requests.post")
    def test_send_discord_notification_with_custom_avatar_and_name(
        self, mock_post, mock_set_cache, mock_get_cache, mock_validate, mock_getenv
    ):
        """Test send_discord_notification with custom avatar and name."""
        mock_getenv.return_value = "https://discord.com/api/webhooks/test"
        mock_validate.return_value = True
        mock_get_cache.return_value = None
        mock_post.return_value.raise_for_status.return_value = None

        send_discord_notification(
            content="Test content",
            avatar_url="https://custom.avatar.com/image.png",
            webhook_name="Custom Name",
        )

        mock_get_cache.assert_called_once_with(notification="Test content")
        mock_set_cache.assert_called_once_with(notification="Test content")
        mock_post.assert_called_once()

        call_args = mock_post.call_args
        data = call_args[1]["json"]
        assert data["avatar_url"] == "https://custom.avatar.com/image.png"
        assert data["username"] == "Custom Name"

    @patch("kernelCI_app.helpers.discordWebhook.os.getenv")
    @patch("kernelCI_app.helpers.discordWebhook.validate_notification")
    @patch("kernelCI_app.helpers.discordWebhook.requests.post")
    @patch("kernelCI_app.helpers.discordWebhook.log_message")
    def test_send_discord_notification_http_error(
        self,
        mock_log_message,
        mock_post,
        mock_validate,
        mock_getenv,
    ):
        """Test send_discord_notification with HTTP error."""
        mock_getenv.return_value = "https://discord.com/api/webhooks/test"
        mock_validate.return_value = True

        error = requests.HTTPError("HTTP error")
        mock_post.return_value.raise_for_status.side_effect = error

        send_discord_notification(embeds=[{"title": "Test embed"}])

        mock_post.assert_called_once()

        mock_log_message.assert_called_once_with(error)
