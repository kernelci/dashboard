from datetime import datetime
from kernelCI_app.typeModels.commonDetails import (
    BuildHistoryItem,
)


class TestBuildHistoryItem:
    """Test cases for BuildHistoryItem class."""

    def test_build_history_item_misc_variations(self):
        """Test BuildHistoryItem with different misc field variations."""
        base_data = {
            "id": "build123",
            "origin": "origin1",
            "architecture": "x86_64",
            "config_name": "config1",
            "config_url": "http://example.com/config",
            "compiler": "gcc",
            "status": "PASS",
            "duration": 300,
            "log_url": "http://example.com/log",
            "start_time": datetime.now(),
            "git_repository_url": "https://git.example.com/repo",
            "git_repository_branch": "main",
        }

        build_with_misc_dict = BuildHistoryItem(
            **base_data, misc={"key": "value", "number": 1}
        )
        assert build_with_misc_dict.misc == {"key": "value", "number": 1}

        build_with_misc_string = BuildHistoryItem(
            **base_data, misc='{"key": "value", "number": 42}'
        )
        assert build_with_misc_string.misc == {"key": "value", "number": 42}

        build_with_misc_invalid_json = BuildHistoryItem(
            **base_data, misc="not_valid_json"
        )
        assert build_with_misc_invalid_json.misc is None

        build_with_misc_none = BuildHistoryItem(**base_data, misc=None)
        assert build_with_misc_none.misc is None

        build_with_misc_int = BuildHistoryItem(**base_data, misc=123)
        assert build_with_misc_int.misc is None
