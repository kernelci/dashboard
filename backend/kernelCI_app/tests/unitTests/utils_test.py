import json
import yaml
from unittest.mock import patch, mock_open
from datetime import timedelta
from django.utils import timezone
from kernelCI_app.utils import (
    create_issue_typed,
    convert_issues_dict_to_list_typed,
    extract_error_message,
    get_query_time_interval,
    get_error_body_response,
    string_to_json,
    is_boot,
    validate_str_to_dict,
    group_status,
    read_yaml_file,
    DEFAULT_QUERY_TIME_INTERVAL,
)
from kernelCI_app.typeModels.issues import Issue
from kernelCI_app.typeModels.common import StatusCount, GroupedStatus
from kernelCI_app.typeModels.treeListing import TestStatusCount


class TestCreateIssueTyped:
    def test_create_issue_typed_with_all_fields(self):
        """Test creating issue with all fields provided."""
        issue_id = "issue123"
        issue_version = 1
        issue_comment = "Test comment"
        issue_report_url = "http://example.com/report"
        starting_count_status = "PASS"

        result = create_issue_typed(
            issue_id=issue_id,
            issue_version=issue_version,
            issue_comment=issue_comment,
            issue_report_url=issue_report_url,
            starting_count_status=starting_count_status,
        )

        assert isinstance(result, Issue)
        assert result.id == issue_id
        assert result.version == issue_version
        assert result.comment == issue_comment
        assert result.report_url == issue_report_url
        assert result.incidents_info.PASS == 1

    def test_create_issue_typed_with_none_values(self):
        """Test creating issue with None values."""
        issue_id = "issue123"
        issue_version = 1

        result = create_issue_typed(
            issue_id=issue_id,
            issue_version=issue_version,
            issue_comment=None,
            issue_report_url=None,
            starting_count_status=None,
        )

        assert isinstance(result, Issue)
        assert result.id == issue_id
        assert result.version == issue_version
        assert result.comment is None
        assert result.report_url is None
        assert result.incidents_info.PASS == 0

    def test_create_issue_typed_with_different_status(self):
        """Test creating issue with different status."""
        issue_id = "issue123"
        issue_version = 1
        starting_count_status = "FAIL"

        result = create_issue_typed(
            issue_id=issue_id,
            issue_version=issue_version,
            issue_comment=None,
            issue_report_url=None,
            starting_count_status=starting_count_status,
        )

        assert result.incidents_info.FAIL == 1


class TestConvertIssuesDictToListTyped:
    def test_convert_issues_dict_to_list_typed_with_dicts(self):
        """Test converting issues dict with dictionary values."""
        issues_dict = {
            "issue1": {
                "id": "issue1",
                "version": 1,
                "comment": "Comment 1",
                "report_url": "http://example.com/1",
                "incidents_info": {
                    "PASS": 5,
                    "FAIL": 2,
                    "ERROR": 0,
                    "SKIP": 0,
                    "MISS": 0,
                    "DONE": 0,
                    "NULL": 0,
                },
            },
            "issue2": {
                "id": "issue2",
                "version": 2,
                "comment": "Comment 2",
                "report_url": "http://example.com/2",
                "incidents_info": {
                    "PASS": 3,
                    "FAIL": 1,
                    "ERROR": 0,
                    "SKIP": 0,
                    "MISS": 0,
                    "DONE": 0,
                    "NULL": 0,
                },
            },
        }

        result = convert_issues_dict_to_list_typed(issues_dict=issues_dict)

        assert len(result) == 2
        assert all(isinstance(issue, Issue) for issue in result)
        assert result[0].id == "issue1"
        assert result[1].id == "issue2"

    def test_convert_issues_dict_to_list_typed_with_issue_objects(self):
        """Test converting issues dict with Issue objects."""
        issue1 = Issue(
            id="issue1",
            version=1,
            comment="Comment 1",
            report_url="http://example.com/1",
            incidents_info=StatusCount(),
        )
        issue2 = Issue(
            id="issue2",
            version=2,
            comment="Comment 2",
            report_url="http://example.com/2",
            incidents_info=StatusCount(),
        )

        issues_dict = {"issue1": issue1, "issue2": issue2}

        result = convert_issues_dict_to_list_typed(issues_dict=issues_dict)

        assert len(result) == 2
        assert result[0] is issue1
        assert result[1] is issue2

    def test_convert_issues_dict_to_list_typed_mixed(self):
        """Test converting issues dict with mixed dict and Issue objects."""
        issue1 = Issue(
            id="issue1",
            version=1,
            comment="Comment 1",
            report_url="http://example.com/1",
            incidents_info=StatusCount(),
        )

        issues_dict = {
            "issue1": issue1,
            "issue2": {
                "id": "issue2",
                "version": 2,
                "comment": "Comment 2",
                "report_url": "http://example.com/2",
                "incidents_info": {
                    "PASS": 3,
                    "FAIL": 1,
                    "ERROR": 0,
                    "SKIP": 0,
                    "MISS": 0,
                    "DONE": 0,
                    "NULL": 0,
                },
            },
        }

        result = convert_issues_dict_to_list_typed(issues_dict=issues_dict)

        assert len(result) == 2
        assert result[0] is issue1
        assert isinstance(result[1], Issue)
        assert result[1].id == "issue2"


class TestExtractErrorMessage:
    def test_extract_error_message_none(self):
        """Test extract_error_message with None input."""
        result = extract_error_message(None)
        assert result == "unknown error"

    def test_extract_error_message_dict_with_error_msg(self):
        """Test extract_error_message with dict containing error_msg."""
        misc = {"error_msg": "Test error message"}
        result = extract_error_message(misc)
        assert result == "Test error message"

    def test_extract_error_message_dict_without_error_msg(self):
        """Test extract_error_message with dict without error_msg."""
        misc = {"other_field": "value"}
        result = extract_error_message(misc)
        assert result == "unknown error"

    def test_extract_error_message_json_string_with_error_msg(self):
        """Test extract_error_message with JSON string containing error_msg."""
        misc = '{"error_msg": "JSON error message"}'
        result = extract_error_message(misc)
        assert result == "JSON error message"

    def test_extract_error_message_json_string_without_error_msg(self):
        """Test extract_error_message with JSON string without error_msg."""
        misc = '{"other_field": "value"}'
        result = extract_error_message(misc)
        assert result == "unknown error"


class TestGetQueryTimeInterval:
    @patch("kernelCI_app.utils.timezone.now")
    def test_get_query_time_interval_no_kwargs(self, mock_now):
        """Test get_query_time_interval with no kwargs."""
        mock_now.return_value = timezone.datetime(2024, 1, 15, 12, 0, 0)

        result = get_query_time_interval()

        expected = mock_now.return_value - timedelta(**DEFAULT_QUERY_TIME_INTERVAL)
        assert result == expected

    @patch("kernelCI_app.utils.timezone.now")
    def test_get_query_time_interval_with_kwargs(self, mock_now):
        """Test get_query_time_interval with kwargs."""
        mock_now.return_value = timezone.datetime(2024, 1, 15, 12, 0, 0)

        result = get_query_time_interval(days=7, hours=12)

        expected = mock_now.return_value - timedelta(days=7, hours=12)
        assert result == expected


class TestGetErrorBodyResponse:
    def test_get_error_body_response(self):
        """Test get_error_body_response."""
        reason = "Test error reason"
        result = get_error_body_response(reason)

        expected = json.dumps({"error": True, "reason": reason}).encode("utf-8")
        assert result == expected

    def test_get_error_body_response_empty_reason(self):
        """Test get_error_body_response with empty reason."""
        reason = ""
        result = get_error_body_response(reason)

        expected = json.dumps({"error": True, "reason": ""}).encode("utf-8")
        assert result == expected


class TestStringToJson:
    @patch("kernelCI_app.utils.log_message")
    def test_string_to_json_valid_json(self, mock_log_message):
        """Test string_to_json with valid JSON."""
        json_string = '{"key": "value", "number": 123}'
        result = string_to_json(json_string)

        expected = {"key": "value", "number": 123}
        assert result == expected
        mock_log_message.assert_not_called()

    @patch("kernelCI_app.utils.log_message")
    def test_string_to_json_invalid_json(self, mock_log_message):
        """Test string_to_json with invalid JSON."""
        json_string = '{"invalid": json}'
        result = string_to_json(json_string)

        assert result is None
        mock_log_message.assert_called_once()

    @patch("kernelCI_app.utils.log_message")
    def test_string_to_json_empty_string(self, mock_log_message):
        """Test string_to_json with empty string."""
        json_string = ""
        result = string_to_json(json_string)

        assert result is None
        mock_log_message.assert_not_called()

    @patch("kernelCI_app.utils.log_message")
    def test_string_to_json_none(self, mock_log_message):
        """Test string_to_json with None."""
        result = string_to_json(None)

        assert result is None
        mock_log_message.assert_not_called()


class TestIsBoot:
    def test_is_boot_none(self):
        """Test is_boot with None."""
        assert is_boot(None) is False

    def test_is_boot_exact_match(self):
        """Test is_boot with exact 'boot' match."""
        assert is_boot("boot") is True

    def test_is_boot_with_dot(self):
        """Test is_boot with path starting with 'boot.'."""
        assert is_boot("boot.test") is True
        assert is_boot("boot.sub.test") is True

    def test_is_boot_other_paths(self):
        """Test is_boot with other paths."""
        assert is_boot("test") is False
        assert is_boot("boots") is False
        assert is_boot("test.boot") is False


class TestValidateStrToDict:
    def test_validate_str_to_dict_with_string(self):
        """Test validate_str_to_dict with JSON string."""
        json_string = '{"key": "value"}'
        result = validate_str_to_dict(json_string)

        assert result == {"key": "value"}

    def test_validate_str_to_dict_with_dict(self):
        """Test validate_str_to_dict with dict."""
        input_dict = {"key": "value"}
        result = validate_str_to_dict(input_dict)

        assert result is input_dict

    def test_validate_str_to_dict_with_other_types(self):
        """Test validate_str_to_dict with other types."""
        assert validate_str_to_dict(123) == 123
        assert validate_str_to_dict([1, 2, 3]) == [1, 2, 3]
        assert validate_str_to_dict("simple string") == "simple string"


class TestGroupStatus:
    def test_group_status_with_status_count(self):
        """Test group_status with StatusCount."""
        status_count = StatusCount()
        status_count.PASS = 10
        status_count.FAIL = 5
        status_count.ERROR = 2
        status_count.SKIP = 1
        status_count.MISS = 1
        status_count.DONE = 1
        status_count.NULL = 1

        result = group_status(status_count)

        expected: GroupedStatus = {
            "success": 10,
            "failed": 5,
            "inconclusive": 6,
        }
        assert result == expected

    def test_group_status_with_test_status_count(self):
        """Test group_status with TestStatusCount."""
        test_status_count = TestStatusCount(
            **{"pass": 8},
            error=1,
            fail=3,
            skip=1,
            miss=1,
            done=1,
            null=1,
        )

        result = group_status(test_status_count)

        expected: GroupedStatus = {
            "success": 8,
            "failed": 3,
            "inconclusive": 5,
        }
        assert result == expected

    @patch("kernelCI_app.utils.log_message")
    def test_group_status_with_invalid_type(self, mock_log_message):
        """Test group_status with invalid type."""
        invalid_object = "invalid"
        result = group_status(invalid_object)

        expected: GroupedStatus = {"success": 0, "failed": 0, "inconclusive": 0}
        assert result == expected
        mock_log_message.assert_called_once()


class TestReadYamlFile:
    def test_read_yaml_file_success(self):
        """Test read_yaml_file with valid YAML file."""
        yaml_content = """
        key1: value1
        key2: value2
        nested:
          key3: value3
        """
        expected_data = {
            "key1": "value1",
            "key2": "value2",
            "nested": {"key3": "value3"},
        }

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("yaml.safe_load", return_value=expected_data):
                result = read_yaml_file(base_dir="/test", file="test.yaml")

        assert result == expected_data

    def test_read_yaml_file_not_found(self):
        """Test read_yaml_file with file not found."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = read_yaml_file(base_dir="/test", file="nonexistent.yaml")

        assert result is None

    def test_read_yaml_file_yaml_error(self):
        """Test read_yaml_file with YAML parsing error."""
        yaml_content = "invalid: yaml: content: ["

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("yaml.safe_load", side_effect=Exception("YAML parsing error")):
                result = read_yaml_file(base_dir="/test", file="invalid.yaml")

        assert result is None

    def test_read_yaml_file_yaml_yamlerror(self):
        """Test read_yaml_file with yaml.YAMLError to cover lines 139-140."""
        yaml_content = "invalid: yaml: content: ["

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch(
                "yaml.safe_load", side_effect=yaml.YAMLError("YAML parsing error")
            ):
                result = read_yaml_file(base_dir="/test", file="invalid.yaml")

        assert result is None

    def test_read_yaml_file_empty_file(self):
        """Test read_yaml_file with empty file."""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("yaml.safe_load", return_value=None):
                result = read_yaml_file(base_dir="/test", file="empty.yaml")

        assert result is None
