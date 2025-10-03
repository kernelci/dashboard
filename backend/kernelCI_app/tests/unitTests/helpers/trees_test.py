from datetime import datetime
from unittest.mock import patch, mock_open
import yaml
from kernelCI_app.helpers.trees import (
    make_tree_identifier_key,
    get_tree_file_data,
    get_tree_url_to_name_map,
    sanitize_tree,
)
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.treeListing import Checkout
from kernelCI_app.tests.unitTests.helpers.fixtures.checkout_data import (
    checkout_data_with_list_tags,
    checkout_data_with_string_tags,
    checkout_data_with_invalid_json_tags,
    checkout_data_with_non_list_json_tags,
)


class TestMakeTreeIdentifierKey:
    def test_make_tree_identifier_key(self):
        """Test make_tree_identifier_key function."""
        result = make_tree_identifier_key(
            tree_name="mainline",
            git_repository_url="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
            git_repository_branch="master",
        )

        expected = "mainline-https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git-master"
        assert result == expected

    def test_make_tree_identifier_key_with_special_chars(self):
        """Test make_tree_identifier_key with special characters."""
        result = make_tree_identifier_key(
            tree_name="stable-5.4",
            git_repository_url="https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git",
            git_repository_branch="linux-5.4.y",
        )

        expected = "stable-5.4-https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git-linux-5.4.y"
        assert result == expected


class TestGetTreeFileData:
    @patch("kernelCI_app.helpers.trees.os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("kernelCI_app.helpers.trees.yaml.safe_load")
    def test_get_tree_file_data_success(self, mock_yaml_load, mock_file, mock_exists):
        """Test get_tree_file_data with successful file read."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            "trees": {"mainline": {"url": "https://git.kernel.org"}}
        }

        result = get_tree_file_data()

        assert result == {"trees": {"mainline": {"url": "https://git.kernel.org"}}}
        mock_file.assert_called_once()
        mock_yaml_load.assert_called_once()

    @patch("kernelCI_app.helpers.trees.os.path.exists")
    def test_get_tree_file_data_file_not_exists(self, mock_exists):
        """Test get_tree_file_data when file doesn't exist."""
        mock_exists.return_value = False

        result = get_tree_file_data()

        assert result == {}

    @patch("kernelCI_app.helpers.trees.os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("kernelCI_app.helpers.trees.yaml.safe_load")
    def test_get_tree_file_data_none_content(
        self, mock_yaml_load, mock_file, mock_exists
    ):
        """Test get_tree_file_data with None content."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = None

        result = get_tree_file_data()

        assert result == {}


class TestGetTreeUrlToNameMap:
    @patch("kernelCI_app.helpers.trees.get_tree_file_data")
    def test_get_tree_url_to_name_map_success(self, mock_get_data):
        """Test get_tree_url_to_name_map with successful data."""
        mock_get_data.return_value = {
            "trees": {
                "mainline": {
                    "url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
                },
                "stable": {
                    "url": "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"
                },
            }
        }

        result = get_tree_url_to_name_map()

        expected = {
            "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git": "mainline",
            "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git": "stable",
        }
        assert result == expected

    @patch("kernelCI_app.helpers.trees.get_tree_file_data")
    def test_get_tree_url_to_name_map_empty_data(self, mock_get_data):
        """Test get_tree_url_to_name_map with empty data."""
        mock_get_data.return_value = {}

        result = get_tree_url_to_name_map()

        assert result == {}

    @patch("kernelCI_app.helpers.trees.get_tree_file_data")
    def test_get_tree_url_to_name_map_no_trees_key(self, mock_get_data):
        """Test get_tree_url_to_name_map without trees key."""
        mock_get_data.return_value = {"other": "data"}

        result = get_tree_url_to_name_map()

        assert result == {}

    @patch("kernelCI_app.helpers.trees.get_tree_file_data")
    def test_get_tree_url_to_name_map_missing_url(self, mock_get_data):
        """Test get_tree_url_to_name_map with missing url in tree data."""
        mock_get_data.return_value = {
            "trees": {
                "mainline": {"name": "mainline"},
                "stable": {
                    "url": "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"
                },
            }
        }

        result = get_tree_url_to_name_map()

        expected = {
            "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git": "stable",
        }
        assert result == expected

    @patch("kernelCI_app.helpers.trees.log_message")
    @patch("kernelCI_app.helpers.trees.get_tree_file_data")
    def test_get_tree_url_to_name_map_yaml_error(self, mock_get_data, mock_log_message):
        """Test get_tree_url_to_name_map with YAML error."""
        error = yaml.YAMLError("YAML parsing error")
        mock_get_data.side_effect = error

        result = get_tree_url_to_name_map()

        assert result == {}
        mock_log_message.assert_called_once_with(error)

    @patch("kernelCI_app.helpers.trees.log_message")
    @patch("kernelCI_app.helpers.trees.get_tree_file_data")
    def test_get_tree_url_to_name_map_file_not_found(
        self, mock_get_data, mock_log_message
    ):
        """Test get_tree_url_to_name_map with FileNotFoundError."""
        error = FileNotFoundError("File not found")
        mock_get_data.side_effect = error

        result = get_tree_url_to_name_map()

        assert result == {}
        mock_log_message.assert_called_once_with(error)


class TestSanitizeTree:
    def test_sanitize_tree_basic(self):
        """Test sanitize_tree with basic data."""
        result = sanitize_tree(checkout_data_with_list_tags)

        assert isinstance(result, Checkout)
        assert result.id == "checkout123"
        assert result.origin == "test"
        assert result.tree_name == "mainline"
        assert isinstance(result.build_status, StatusCount)
        assert result.build_status.PASS == 10
        assert result.build_status.FAIL == 2
        assert result.test_status.pass_count == 50
        assert result.test_status.fail_count == 5
        assert result.boot_status.pass_count == 20
        assert result.boot_status.fail_count == 1
        assert result.git_commit_tags == [["v5.4"], ["v5.4.1"]]
        assert result.start_time == datetime(2023, 1, 1, 0, 0)
        assert result.origin_builds_finish_time == datetime(2023, 1, 1, 1, 0)
        assert result.origin_tests_finish_time == datetime(2023, 1, 1, 2, 0)

    def test_sanitize_tree_with_string_git_commit_tags(self):
        """Test sanitize_tree with string git_commit_tags."""
        result = sanitize_tree(checkout_data_with_string_tags)

        assert result.git_commit_tags == [["v5.4"], ["v5.4.1"]]

    def test_sanitize_tree_with_invalid_json_git_commit_tags(self):
        """Test sanitize_tree with invalid JSON git_commit_tags."""
        result = sanitize_tree(checkout_data_with_invalid_json_tags)

        assert result.git_commit_tags == []

    def test_sanitize_tree_with_non_list_json_git_commit_tags(self):
        """Test sanitize_tree with non-list JSON git_commit_tags."""
        result = sanitize_tree(checkout_data_with_non_list_json_tags)

        assert result.git_commit_tags == []
