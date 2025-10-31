import os
import yaml
import pytest
from unittest.mock import patch
from kernelCI_app.management.commands.helpers.file_utils import (
    load_tree_names,
    move_file_to_failed_dir,
    verify_dir,
    verify_spool_dirs,
)
from kernelCI_app.tests.unitTests.helpers.fixtures.file_utils_data import (
    TREES_PATH_TESTING,
    BASE_TREES_FILE,
    EXPECTED_PARSED_TREES_FILE,
    BASE_FILE_NAME,
    NONEXISTING_FILE_NAME,
    TESTING_FAILED_DIR,
    EXISTING_DIRECTORY,
    MISSING_DIRECTORY,
    DENIED_DIRECTORY,
    NOT_A_DIRECTORY,
    UNACCESSIBLE_DIRECTORY,
    SPOOL_DIR_TESTING,
    FAIL_SPOOL_SUBDIR,
    ARCHIVE_SPOOL_SUBDIR,
)


class TestLoadTreeNames:
    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_tree_names_with_default_file(self, mock_yaml_load, mock_open):
        """Test load_tree_names using default TREES_FILE constant."""
        mock_yaml_data = BASE_TREES_FILE
        mock_yaml_load.return_value = mock_yaml_data

        result = load_tree_names()

        mock_open.assert_called_once_with("/app/trees.yaml", "r", encoding="utf-8")
        mock_yaml_load.assert_called_once()
        assert result == EXPECTED_PARSED_TREES_FILE

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_tree_names_with_valid_yaml(self, mock_yaml_load, mock_open):
        """Test load_tree_names with valid YAML data."""
        mock_yaml_load.return_value = BASE_TREES_FILE

        result = load_tree_names(TREES_PATH_TESTING)

        mock_open.assert_called_once_with(TREES_PATH_TESTING, "r", encoding="utf-8")
        mock_yaml_load.assert_called_once()
        assert result == EXPECTED_PARSED_TREES_FILE

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_tree_names_with_empty_trees(self, mock_yaml_load, mock_open):
        """Test load_tree_names with empty trees section."""
        empty_trees_file = {"trees": {}}
        mock_yaml_load.return_value = empty_trees_file

        result = load_tree_names(TREES_PATH_TESTING)

        mock_open.assert_called_once_with(TREES_PATH_TESTING, "r", encoding="utf-8")
        mock_yaml_load.assert_called_once()
        assert result == {}

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_tree_names_with_no_trees_key(self, mock_yaml_load, mock_open):
        """Test load_tree_names with YAML data missing trees key."""
        wrong_trees_file = {"not_trees": "any_value"}
        mock_yaml_load.return_value = wrong_trees_file

        result = load_tree_names(TREES_PATH_TESTING)

        mock_open.assert_called_once_with(TREES_PATH_TESTING, "r", encoding="utf-8")
        mock_yaml_load.assert_called_once()
        assert result == {}

    @patch("builtins.open")
    def test_load_tree_names_file_not_found(self, mock_open):
        """Test load_tree_names when file doesn't exist."""
        mock_open.side_effect = FileNotFoundError("File not found")
        with pytest.raises(FileNotFoundError):
            load_tree_names("/nonexistent/trees.yaml")

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_tree_names_invalid_yaml(self, mock_yaml_load, _):
        """Test load_tree_names with invalid YAML content."""
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")
        with pytest.raises(yaml.YAMLError):
            load_tree_names(TREES_PATH_TESTING)


class TestMoveFileToFailedDir:
    @patch("os.rename")
    @patch("os.path.basename")
    @patch("os.path.join")
    def test_move_file_to_failed_dir_success(
        self, mock_join, mock_basename, mock_rename
    ):
        """Test successful file move to failed directory."""
        mock_basename.return_value = BASE_FILE_NAME
        mock_join.return_value = f"{TESTING_FAILED_DIR}/{BASE_FILE_NAME}"

        move_file_to_failed_dir(BASE_FILE_NAME, TESTING_FAILED_DIR)

        mock_basename.assert_called_once_with(BASE_FILE_NAME)
        mock_join.assert_called_once_with(TESTING_FAILED_DIR, BASE_FILE_NAME)
        mock_rename.assert_called_once_with(BASE_FILE_NAME, mock_join.return_value)

    @patch("os.rename")
    @patch("os.path.basename")
    @patch("os.path.join")
    @patch("kernelCI_app.management.commands.helpers.file_utils.logger")
    def test_move_file_to_failed_dir_file_not_found(
        self, mock_logger, mock_join, mock_basename, mock_rename
    ):
        """Test file move when source file doesn't exist."""
        mock_rename.side_effect = FileNotFoundError("File not found")
        mock_rename.return_value = NONEXISTING_FILE_NAME
        mock_join.return_value = f"{TESTING_FAILED_DIR}/{BASE_FILE_NAME}"

        with pytest.raises(FileNotFoundError):
            move_file_to_failed_dir(NONEXISTING_FILE_NAME, TESTING_FAILED_DIR)

        mock_logger.error.assert_called_once_with(
            "Error moving file %s to failed directory: %s",
            mock_rename.return_value,
            mock_rename.side_effect,
        )


class TestVerifyDir:
    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.access")
    @patch("kernelCI_app.management.commands.helpers.file_utils.logger")
    def test_verify_dir_valid_directory(
        self, mock_logger, mock_access, mock_isdir, mock_exists
    ):
        """Test verify_dir with valid, writable directory."""
        mock_access.return_value = True
        mock_isdir.return_value = True
        mock_exists.return_value = True

        verify_dir(EXISTING_DIRECTORY)

        mock_exists.assert_called_once_with(EXISTING_DIRECTORY)
        mock_isdir.assert_called_once_with(EXISTING_DIRECTORY)
        mock_access.assert_called_once_with(EXISTING_DIRECTORY, os.W_OK)
        mock_logger.info.assert_called_once_with(
            "Directory %s is valid and writable", EXISTING_DIRECTORY
        )

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("os.path.isdir")
    @patch("os.access")
    @patch("kernelCI_app.management.commands.helpers.file_utils.logger")
    def test_verify_dir_creates_missing_directory(
        self, mock_logger, mock_access, mock_isdir, mock_makedirs, mock_exists
    ):
        """Test verify_dir creates valid but missing directory."""
        mock_exists.return_value = False
        mock_access.return_value = True
        mock_isdir.return_value = True

        verify_dir(MISSING_DIRECTORY)

        mock_exists.assert_called_once_with(MISSING_DIRECTORY)
        mock_makedirs.assert_called_once_with(MISSING_DIRECTORY)
        mock_logger.info.assert_any_call("Directory %s created", MISSING_DIRECTORY)
        mock_logger.info.assert_any_call(
            "Directory %s is valid and writable", MISSING_DIRECTORY
        )

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("kernelCI_app.management.commands.helpers.file_utils.logger")
    def test_verify_dir_fails_to_create_directory(
        self, mock_logger, mock_makedirs, mock_exists
    ):
        """Test verify_dir when directory creation fails."""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        mock_exists.return_value = False

        with pytest.raises(PermissionError):
            verify_dir(DENIED_DIRECTORY)

        mock_exists.assert_called_once_with(DENIED_DIRECTORY)
        mock_makedirs.assert_called_once_with(DENIED_DIRECTORY)
        assert mock_logger.error.call_count == 2
        mock_logger.error.assert_any_call(
            "Directory %s does not exist", DENIED_DIRECTORY
        )
        mock_logger.error.assert_any_call(
            "Error creating directory %s: %s",
            DENIED_DIRECTORY,
            mock_makedirs.side_effect,
        )

    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_verify_dir_path_is_not_directory(self, mock_isdir, mock_exists):
        """Test verify_dir when path exists but is not a directory."""
        mock_isdir.return_value = False
        mock_exists.return_value = True

        with pytest.raises(
            Exception, match=f"Directory {NOT_A_DIRECTORY} is not a directory"
        ):
            verify_dir(NOT_A_DIRECTORY)

        mock_exists.assert_called_once_with(NOT_A_DIRECTORY)
        mock_isdir.assert_called_once_with(NOT_A_DIRECTORY)

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.access")
    def test_verify_dir_not_writable(self, mock_access, mock_isdir, mock_exists):
        """Test verify_dir when directory is not writable."""
        mock_access.return_value = False
        mock_isdir.return_value = True
        mock_exists.return_value = True

        with pytest.raises(
            Exception, match=f"Directory {UNACCESSIBLE_DIRECTORY} is not writable"
        ):
            verify_dir(UNACCESSIBLE_DIRECTORY)

        mock_exists.assert_called_once_with(UNACCESSIBLE_DIRECTORY)
        mock_isdir.assert_called_once_with(UNACCESSIBLE_DIRECTORY)
        mock_access.assert_called_once_with(UNACCESSIBLE_DIRECTORY, os.W_OK)


class TestVerifySpoolDirs:
    @patch("kernelCI_app.management.commands.helpers.file_utils.verify_dir")
    @patch("os.path.join")
    def test_verify_spool_dirs_success(self, mock_join, mock_verify_dir):
        """Test verify_spool_dirs with successful directory verification."""
        joined_fail_dir = "/".join([SPOOL_DIR_TESTING, FAIL_SPOOL_SUBDIR])
        joined_archive_dir = "/".join([SPOOL_DIR_TESTING, ARCHIVE_SPOOL_SUBDIR])
        mock_join.side_effect = [joined_fail_dir, joined_archive_dir]

        verify_spool_dirs(SPOOL_DIR_TESTING)

        assert mock_join.call_count == 2
        mock_join.assert_any_call(SPOOL_DIR_TESTING, FAIL_SPOOL_SUBDIR)
        mock_join.assert_any_call(SPOOL_DIR_TESTING, ARCHIVE_SPOOL_SUBDIR)

        assert mock_verify_dir.call_count == 3
        mock_verify_dir.assert_any_call(SPOOL_DIR_TESTING)
        mock_verify_dir.assert_any_call(joined_fail_dir)
        mock_verify_dir.assert_any_call(joined_archive_dir)

    @patch("kernelCI_app.management.commands.helpers.file_utils.verify_dir")
    @patch("os.path.join")
    def test_verify_spool_dirs_join_failure(self, mock_join, mock_verify_dir):
        """Test verify_spool_dirs when os.path.join fails."""
        mock_join.side_effect = OSError("Join operation failed")

        with pytest.raises(OSError):
            verify_spool_dirs(SPOOL_DIR_TESTING)

        mock_join.assert_called_once_with(SPOOL_DIR_TESTING, FAIL_SPOOL_SUBDIR)
        mock_verify_dir.assert_not_called()

    @patch("kernelCI_app.management.commands.helpers.file_utils.verify_dir")
    @patch("os.path.join")
    def test_verify_spool_dirs_verify_spool_dir_fails(self, mock_join, mock_verify_dir):
        """Test verify_spool_dirs when spool directory verification fails."""
        joined_fail_dir = "/".join([SPOOL_DIR_TESTING, FAIL_SPOOL_SUBDIR])
        joined_archive_dir = "/".join([SPOOL_DIR_TESTING, ARCHIVE_SPOOL_SUBDIR])
        mock_join.side_effect = [joined_fail_dir, joined_archive_dir]

        # Meant to represent any kind of failure in verify_dir
        mock_verify_dir.side_effect = Exception("Spool directory verification failed")

        with pytest.raises(Exception, match="Spool directory verification failed"):
            verify_spool_dirs(SPOOL_DIR_TESTING)

        assert mock_join.call_count == 2
        mock_join.assert_any_call(SPOOL_DIR_TESTING, FAIL_SPOOL_SUBDIR)
        mock_join.assert_any_call(SPOOL_DIR_TESTING, ARCHIVE_SPOOL_SUBDIR)

        mock_verify_dir.assert_called_once_with(SPOOL_DIR_TESTING)
