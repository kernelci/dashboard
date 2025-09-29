from unittest.mock import patch
from kernelCI_app.helpers.system import get_running_instance
from kernelCI_app.constants.general import PRODUCTION_HOST


class TestGetRunningInstance:
    @patch("kernelCI_app.helpers.system.settings")
    def test_get_running_instance_production(self, mock_settings):
        """Test get_running_instance returns 'production' when PRODUCTION_HOST is in CORS_ALLOWED_ORIGINS."""
        mock_settings.CORS_ALLOWED_ORIGINS = [PRODUCTION_HOST, "https://other.com"]
        mock_settings.DEBUG = False

        result = get_running_instance()

        assert result == "production"

    @patch("kernelCI_app.helpers.system.settings")
    def test_get_running_instance_production_with_debug_true(self, mock_settings):
        """Test get_running_instance returns 'production' when production CORS is set but DEBUG is True."""
        mock_settings.CORS_ALLOWED_ORIGINS = [PRODUCTION_HOST]
        mock_settings.DEBUG = True

        result = get_running_instance()

        assert result == "production"

    @patch("kernelCI_app.helpers.system.settings")
    def test_get_running_instance_staging(self, mock_settings):
        """Test get_running_instance returns 'staging' when DEBUG is False and not production."""
        mock_settings.CORS_ALLOWED_ORIGINS = ["https://staging.com"]
        mock_settings.DEBUG = False

        result = get_running_instance()

        assert result == "staging"

    @patch("kernelCI_app.helpers.system.settings")
    def test_get_running_instance_none_when_debug_true(self, mock_settings):
        """Test get_running_instance returns None when DEBUG is True."""
        mock_settings.CORS_ALLOWED_ORIGINS = ["https://staging.com"]
        mock_settings.DEBUG = True

        result = get_running_instance()

        assert result is None

    @patch("kernelCI_app.helpers.system.settings")
    def test_get_running_instance_none_when_no_cors_attr(self, mock_settings):
        """Test get_running_instance returns None when CORS_ALLOWED_ORIGINS attribute doesn't exist."""
        delattr(mock_settings, "CORS_ALLOWED_ORIGINS")
        mock_settings.DEBUG = True

        result = get_running_instance()

        assert result is None

    @patch("kernelCI_app.helpers.system.settings")
    def test_get_running_instance_none_when_no_debug_attr(self, mock_settings):
        """Test get_running_instance returns None when DEBUG attribute doesn't exist."""
        mock_settings.CORS_ALLOWED_ORIGINS = ["https://staging.com"]
        delattr(mock_settings, "DEBUG")

        result = get_running_instance()

        assert result is None
