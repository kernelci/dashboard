from unittest.mock import patch
from kernelCI_app.helpers.misc import (
    handle_misc,
    misc_value_or_default,
    Misc,
)
from kernelCI_app.helpers.filters import UNKNOWN_STRING


class TestHandleMisc:
    @patch("kernelCI_app.helpers.misc.string_to_json")
    def test_handle_misc_with_string(self, mock_string_to_json):
        """Test handle_misc with string input."""
        mock_string_to_json.return_value = {"platform": "x86_64"}

        result = handle_misc('{"platform": "x86_64"}')

        mock_string_to_json.assert_called_once_with('{"platform": "x86_64"}')
        assert result == {"platform": "x86_64"}

    @patch("kernelCI_app.helpers.misc.string_to_json")
    def test_handle_misc_with_invalid_string(self, mock_string_to_json):
        """Test handle_misc with invalid JSON string."""
        mock_string_to_json.return_value = None

        result = handle_misc("invalid json")

        assert result is None

    def test_handle_misc_with_dict(self):
        """Test handle_misc with dict input."""
        misc_dict = {"platform": "arm64"}

        result = handle_misc(misc_dict)

        assert result == {"platform": "arm64"}

    def test_handle_misc_with_dict_missing_platform(self):
        """Test handle_misc with dict missing platform key."""
        misc_dict = {"other": "value"}

        result = handle_misc(misc_dict)

        assert result == {"platform": UNKNOWN_STRING}

    def test_handle_misc_with_none(self):
        """Test handle_misc with None input."""
        result = handle_misc(None)

        assert result is None

    def test_handle_misc_with_other_type(self):
        """Test handle_misc with other type input."""
        result = handle_misc(123)

        assert result is None


class TestMiscValueOrDefault:
    def test_misc_value_or_default_with_valid_misc(self):
        """Test misc_value_or_default with valid misc."""
        misc: Misc = {"platform": "x86_64"}

        result = misc_value_or_default(misc)

        assert result == misc

    def test_misc_value_or_default_with_none(self):
        """Test misc_value_or_default with None."""
        result = misc_value_or_default(None)

        expected: Misc = {"platform": UNKNOWN_STRING}
        assert result == expected

    def test_misc_value_or_default_with_empty_dict(self):
        """Test misc_value_or_default with empty dict."""
        misc: Misc = {}

        result = misc_value_or_default(misc)

        assert result == misc
