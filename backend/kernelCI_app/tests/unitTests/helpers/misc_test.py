from unittest.mock import patch
from kernelCI_app.helpers.misc import (
    handle_environment_misc,
    handle_build_misc,
    env_misc_value_or_default,
    build_misc_value_or_default,
    EnvironmentMisc,
    BuildMisc,
)
from kernelCI_app.helpers.filters import UNKNOWN_STRING


class TestHandleEnvironmentMisc:
    @patch("kernelCI_app.helpers.misc.string_to_json")
    def test_handle_environment_misc_with_string(self, mock_string_to_json):
        """Test handle_environment_misc with string input."""
        mock_string_to_json.return_value = {"platform": "x86_64"}

        result = handle_environment_misc('{"platform": "x86_64"}')

        mock_string_to_json.assert_called_once_with('{"platform": "x86_64"}')
        assert result == {"platform": "x86_64"}

    @patch("kernelCI_app.helpers.misc.string_to_json")
    def test_handle_environment_misc_with_invalid_string(self, mock_string_to_json):
        """Test handle_environment_misc with invalid JSON string."""
        mock_string_to_json.return_value = None

        result = handle_environment_misc("invalid json")

        assert result is None

    def test_handle_environment_misc_with_dict(self):
        """Test handle_environment_misc with dict input."""
        misc_dict = {"platform": "arm64"}

        result = handle_environment_misc(misc_dict)

        assert result == {"platform": "arm64"}

    def test_handle_environment_misc_with_dict_missing_platform(self):
        """Test handle_environment_misc with dict missing platform key."""
        misc_dict = {"other": "value"}

        result = handle_environment_misc(misc_dict)

        assert result == {"platform": UNKNOWN_STRING}

    def test_handle_environment_misc_with_none(self):
        """Test handle_environment_misc with None input."""
        result = handle_environment_misc(None)

        assert result is None

    def test_handle_environment_misc_with_other_type(self):
        """Test handle_environment_misc with other type input."""
        result = handle_environment_misc(123)

        assert result is None


class TestHandleBuildMisc:
    @patch("kernelCI_app.helpers.misc.string_to_json")
    def test_handle_build_misc_with_string(self, mock_string_to_json):
        """Test handle_build_misc with string input."""
        mock_string_to_json.return_value = {"platform": "x86_64"}

        result = handle_build_misc('{"platform": "x86_64"}')

        mock_string_to_json.assert_called_once_with('{"platform": "x86_64"}')
        assert result == {"platform": "x86_64"}

    @patch("kernelCI_app.helpers.misc.string_to_json")
    def test_handle_build_misc_with_invalid_string(self, mock_string_to_json):
        """Test handle_build_misc with invalid JSON string."""
        mock_string_to_json.return_value = None

        result = handle_build_misc("invalid json")

        assert result is None

    def test_handle_build_misc_with_dict(self):
        """Test handle_build_misc with dict input."""
        misc_dict = {"platform": "arm64"}

        result = handle_build_misc(misc_dict)

        assert result == {"platform": "arm64"}

    def test_handle_build_misc_with_dict_missing_platform(self):
        """Test handle_build_misc with dict missing platform key."""
        misc_dict = {"other": "value"}

        result = handle_build_misc(misc_dict)

        assert result == {"platform": UNKNOWN_STRING}

    def test_handle_build_misc_with_none(self):
        """Test handle_build_misc with None input."""
        result = handle_build_misc(None)

        assert result is None

    def test_handle_build_misc_with_other_type(self):
        """Test handle_build_misc with other type input."""
        result = handle_build_misc(123)

        assert result is None


class TestEnvMiscValueOrDefault:
    def test_env_misc_value_or_default_with_valid_misc(self):
        """Test env_misc_value_or_default with valid misc."""
        misc: EnvironmentMisc = {"platform": "x86_64"}

        result = env_misc_value_or_default(misc)

        assert result == misc

    def test_env_misc_value_or_default_with_none(self):
        """Test env_misc_value_or_default with None."""
        result = env_misc_value_or_default(None)

        expected: EnvironmentMisc = {"platform": UNKNOWN_STRING}
        assert result == expected

    def test_env_misc_value_or_default_with_empty_dict(self):
        """Test env_misc_value_or_default with empty dict."""
        misc: EnvironmentMisc = {}

        result = env_misc_value_or_default(misc)

        assert result == misc


class TestBuildMiscValueOrDefault:
    def test_build_misc_value_or_default_with_valid_misc(self):
        """Test build_misc_value_or_default with valid misc."""
        misc: BuildMisc = {"platform": "arm64"}

        result = build_misc_value_or_default(misc)

        assert result == misc

    def test_build_misc_value_or_default_with_none(self):
        """Test build_misc_value_or_default with None."""
        result = build_misc_value_or_default(None)

        expected: BuildMisc = {"platform": UNKNOWN_STRING}
        assert result == expected

    def test_build_misc_value_or_default_with_empty_dict(self):
        """Test build_misc_value_or_default with empty dict."""
        misc: BuildMisc = {}

        result = build_misc_value_or_default(misc)

        assert result == misc
