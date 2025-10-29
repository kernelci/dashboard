import pytest
from unittest.mock import patch, MagicMock
from kernelCI_app.helpers.filters import (
    is_status_failure,
    is_known_issue,
    is_unknown_build_issue,
    is_exclusively_build_issue,
    is_exclusively_test_issue,
    is_issue_from_test,
    is_issue_from_build,
    verify_issue_in_filter,
    is_issue_filtered_out,
    should_filter_test_issue,
    should_filter_build_issue,
    should_increment_test_issue,
    should_increment_build_issue,
    to_int_or_default,
    FilterParams,
    InvalidComparisonOPError,
)
from kernelCI_app.constants.general import UNCATEGORIZED_STRING
from kernelCI_app.tests.unitTests.helpers.fixtures.filter_fixtures import (
    BOOT_FILTER_DATA_SCENARIOS,
    FILTER_DATA_SCENARIOS,
    FILTER_OBJECTS,
    FILTER_BODY_DATA,
    filter_params_with_exact_filter,
    filter_params_with_filters,
    filter_params_with_invalid_op,
    MATCHING_ISSUE_FILTERS,
    mock_request,
    mock_request_with_filters,
    mock_request_with_multiple_filters,
    mock_request_with_string_filter,
    mock_request_with_regex_filter,
    mock_request_with_invalid_param,
)


class TestIsStatusFailure:
    def test_is_status_failure_with_failure_status(self):
        """Test is_status_failure with failure status."""
        result = is_status_failure("FAIL")
        assert result is True

    def test_is_status_failure_with_success_status(self):
        """Test is_status_failure with success status."""
        result = is_status_failure("PASS")
        assert result is False

    def test_is_status_failure_with_custom_fail_list(self):
        """Test is_status_failure with custom fail list."""
        custom_fail_list = ["CUSTOM_FAIL", "ERROR"]
        result = is_status_failure("CUSTOM_FAIL", custom_fail_list)
        assert result is True

    def test_is_status_failure_with_custom_fail_list_no_match(self):
        """Test is_status_failure with custom fail list no match."""
        custom_fail_list = ["CUSTOM_FAIL", "ERROR"]
        result = is_status_failure("PASS", custom_fail_list)
        assert result is False


class TestIsKnownIssue:
    def test_is_known_issue_with_valid_issue(self):
        """Test is_known_issue with valid issue."""
        result = is_known_issue("issue123", 1)
        assert result is True

    def test_is_known_issue_with_none_id(self):
        """Test is_known_issue with None issue_id."""
        result = is_known_issue(None, 1)
        assert result is False

    def test_is_known_issue_with_none_version(self):
        """Test is_known_issue with None issue_version."""
        result = is_known_issue("issue123", None)
        assert result is False

    def test_is_known_issue_with_uncategorized(self):
        """Test is_known_issue with uncategorized string."""
        result = is_known_issue(UNCATEGORIZED_STRING, 1)
        assert result is False

    def test_is_known_issue_with_both_none(self):
        """Test is_known_issue with both None."""
        result = is_known_issue(None, None)
        assert result is False


class TestIsUnknownBuildIssue:
    def test_is_unknown_build_issue_with_unknown_issue(self):
        """Test is_unknown_build_issue with unknown issue."""
        result = is_unknown_build_issue(None, None, None)
        assert result is True

    def test_is_unknown_build_issue_with_known_issue(self):
        """Test is_unknown_build_issue with known issue."""
        result = is_unknown_build_issue("issue123", 1, None)
        assert result is False

    def test_is_unknown_build_issue_with_test_incident(self):
        """Test is_unknown_build_issue with test incident."""
        result = is_unknown_build_issue(None, None, "test123")
        assert result is False

    def test_is_unknown_build_issue_with_uncategorized(self):
        """Test is_unknown_build_issue with uncategorized."""
        result = is_unknown_build_issue(UNCATEGORIZED_STRING, None, None)
        assert result is True


class TestIsExclusivelyBuildIssue:
    def test_is_exclusively_build_issue_with_known_issue_no_test(self):
        """Test is_exclusively_build_issue with known issue no test."""
        result = is_exclusively_build_issue("issue123", 1, None)
        assert result is True

    def test_is_exclusively_build_issue_with_known_issue_with_test(self):
        """Test is_exclusively_build_issue with known issue with test."""
        result = is_exclusively_build_issue("issue123", 1, "test123")
        assert result is False

    def test_is_exclusively_build_issue_with_unknown_issue(self):
        """Test is_exclusively_build_issue with unknown issue."""
        result = is_exclusively_build_issue(None, None, None)
        assert result is False

    def test_is_exclusively_build_issue_with_unknown_issue_with_test(self):
        """Test is_exclusively_build_issue with unknown issue but with test."""
        result = is_exclusively_build_issue(None, None, "test123")
        assert result is False


class TestIsExclusivelyTestIssue:
    def test_is_exclusively_test_issue_with_known_issue_with_test(self):
        """Test is_exclusively_test_issue with known issue with test."""
        result = is_exclusively_test_issue(
            issue_id="issue123", issue_version=1, incident_test_id="test123"
        )
        assert result is True

    def test_is_exclusively_test_issue_with_known_issue_no_test(self):
        """Test is_exclusively_test_issue with known issue no test."""
        result = is_exclusively_test_issue(
            issue_id="issue123", issue_version=1, incident_test_id=None
        )
        assert result is False

    def test_is_exclusively_test_issue_with_unknown_issue(self):
        """Test is_exclusively_test_issue with unknown issue."""
        result = is_exclusively_test_issue(
            issue_id=None, issue_version=None, incident_test_id="test123"
        )
        assert result is False

    def test_is_exclusively_test_issue_with_unknown_issue_no_test(self):
        """Test is_exclusively_test_issue with unknown issue and no test."""
        result = is_exclusively_test_issue(
            issue_id=None, issue_version=None, incident_test_id=None
        )
        assert result is False


class TestIsIssueFromTest:
    def test_is_issue_from_test_with_test_incident(self):
        """Test is_issue_from_test with test incident."""
        result = is_issue_from_test(
            incident_test_id="test123", issue_id="issue123", issue_version=1
        )
        assert result is True

    def test_is_issue_from_test_with_unknown_issue(self):
        """Test is_issue_from_test with unknown issue."""
        result = is_issue_from_test(
            incident_test_id=None, issue_id=None, issue_version=None
        )
        assert result is True

    def test_is_issue_from_test_with_known_issue_no_test(self):
        """Test is_issue_from_test with known issue no test."""
        result = is_issue_from_test(
            incident_test_id=None, issue_id="issue123", issue_version=1
        )
        assert result is False


class TestIsIssueFromBuild:
    def test_is_issue_from_build_with_no_test_incident(self):
        """Test is_issue_from_build with no test incident."""
        result = is_issue_from_build(
            issue_id="issue123", issue_version=1, incident_test_id=None
        )
        assert result is True

    def test_is_issue_from_build_with_unknown_issue(self):
        """Test is_issue_from_build with unknown issue."""
        result = is_issue_from_build(
            issue_id=None, issue_version=None, incident_test_id="test123"
        )
        assert result is True

    def test_is_issue_from_build_with_known_issue_with_test(self):
        """Test is_issue_from_build with known issue with test."""
        result = is_issue_from_build(
            issue_id="issue123", issue_version=1, incident_test_id="test123"
        )
        assert result is False


class TestVerifyIssueInFilter:
    def test_verify_issue_in_filter_with_uncategorized(self):
        """Test verify_issue_in_filter with uncategorized."""
        filter_data = FILTER_DATA_SCENARIOS["uncategorized"]
        result = verify_issue_in_filter(**filter_data)
        assert result is True

    def test_verify_issue_in_filter_with_tuple_match(self):
        """Test verify_issue_in_filter with tuple match."""
        filter_data = FILTER_DATA_SCENARIOS["tuple_match"]
        result = verify_issue_in_filter(**filter_data)
        assert result is True

    def test_verify_issue_in_filter_with_tuple_no_match_id(self):
        """Test verify_issue_in_filter with tuple no match ID."""
        filter_data = FILTER_DATA_SCENARIOS["tuple_no_match_id"]
        result = verify_issue_in_filter(**filter_data)
        assert result is False

    def test_verify_issue_in_filter_with_tuple_no_match_version(self):
        """Test verify_issue_in_filter with tuple no match version."""
        filter_data = FILTER_DATA_SCENARIOS["tuple_no_match_version"]
        result = verify_issue_in_filter(**filter_data)
        assert result is False

    def test_verify_issue_in_filter_with_uncategorized_issue(self):
        """Test verify_issue_in_filter with uncategorized issue."""
        filter_data = FILTER_DATA_SCENARIOS["uncategorized_issue"]
        result = verify_issue_in_filter(**filter_data)
        assert result is False


class TestIsIssueFilteredOut:
    def test_is_issue_filtered_out_with_empty_filters(self):
        """Test is_issue_filtered_out with empty filters."""
        result = is_issue_filtered_out(
            issue_id="issue123", issue_filters=set(), issue_version=1
        )
        assert result is True

    def test_is_issue_filtered_out_with_matching_filter(self):
        """Test is_issue_filtered_out with matching filter."""
        result = is_issue_filtered_out(
            issue_id="issue123", issue_filters=MATCHING_ISSUE_FILTERS, issue_version=1
        )
        assert result is False

    def test_is_issue_filtered_out_with_non_matching_filter(self):
        """Test is_issue_filtered_out with non-matching filter."""
        result = is_issue_filtered_out(
            issue_id="issue123",
            issue_filters={("issue456", 2), ("issue789", 3)},
            issue_version=1,
        )
        assert result is True


class TestShouldFilterTestIssue:
    def test_should_filter_test_issue_with_no_filters(self):
        """Test should_filter_test_issue with no filters."""
        result = should_filter_test_issue(
            issue_filters=set(),
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is False

    def test_should_filter_test_issue_with_uncategorized_filter(self):
        """Test should_filter_test_issue with uncategorized filter."""
        result = should_filter_test_issue(
            issue_filters={UNCATEGORIZED_STRING},
            issue_id="issue123",
            issue_version=1,
            incident_test_id=None,
        )
        assert result is False

    def test_should_filter_test_issue_with_exclusively_build_issue(self):
        """Test should_filter_test_issue with exclusively build issue."""
        result = should_filter_test_issue(
            issue_filters=MATCHING_ISSUE_FILTERS,
            issue_id="issue123",
            issue_version=1,
            incident_test_id=None,
        )
        assert result is True

    def test_should_filter_test_issue_with_matching_filter(self):
        """Test should_filter_test_issue with matching filter."""
        result = should_filter_test_issue(
            issue_filters=MATCHING_ISSUE_FILTERS,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is False


class TestShouldFilterBuildIssue:
    def test_should_filter_build_issue_with_no_filters(self):
        """Test should_filter_build_issue with no filters."""
        result = should_filter_build_issue(
            issue_filters=set(),
            issue_id="issue123",
            issue_version=1,
            incident_test_id=None,
            build_status="PASS",
        )
        assert result is False

    def test_should_filter_build_issue_with_non_failure_status(self):
        """Test should_filter_build_issue with non-failure status."""
        filters = {("issue123", 1)}
        result = should_filter_build_issue(
            issue_filters=filters,
            issue_id="issue123",
            issue_version=1,
            incident_test_id=None,
            build_status="PASS",
        )
        assert result is True

    def test_should_filter_build_issue_with_exclusively_test_issue(self):
        """Test should_filter_build_issue with exclusively test issue."""
        filters = {UNCATEGORIZED_STRING}
        result = should_filter_build_issue(
            issue_filters=filters,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
            build_status="FAIL",
        )
        assert result is False

    def test_should_filter_build_issue_with_unknown_build_issue(self):
        """Test should_filter_build_issue with unknown build issue."""
        filters = {UNCATEGORIZED_STRING}
        result = should_filter_build_issue(
            issue_filters=filters,
            issue_id=None,
            issue_version=None,
            incident_test_id=None,
            build_status="FAIL",
        )
        assert result is False


class TestShouldIncrementTestIssue:
    def test_should_increment_test_issue_with_exclusively_build_issue(self):
        """Test should_increment_test_issue with exclusively build issue."""
        result = should_increment_test_issue(
            issue_id="issue123", issue_version=1, incident_test_id=None
        )
        assert result == (UNCATEGORIZED_STRING, None, False)

    def test_should_increment_test_issue_with_test_issue(self):
        """Test should_increment_test_issue with test issue."""
        result = should_increment_test_issue(
            issue_id="issue123", issue_version=1, incident_test_id="test123"
        )
        assert result == ("issue123", 1, True)

    def test_should_increment_test_issue_with_unknown_issue(self):
        """Test should_increment_test_issue with unknown issue."""
        result = should_increment_test_issue(
            issue_id=None, issue_version=None, incident_test_id="test123"
        )
        assert result == (None, None, True)


class TestShouldIncrementBuildIssue:
    def test_should_increment_build_issue_with_exclusively_test_issue(self):
        """Test should_increment_build_issue with exclusively test issue."""
        result = should_increment_build_issue(
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
            build_status="FAIL",
        )
        assert result == (UNCATEGORIZED_STRING, None, False)

    def test_should_increment_build_issue_with_build_issue_failure(self):
        """Test should_increment_build_issue with build issue failure."""
        result = should_increment_build_issue(
            issue_id="issue123",
            issue_version=1,
            incident_test_id=None,
            build_status="FAIL",
        )
        assert result == ("issue123", 1, True)

    def test_should_increment_build_issue_with_build_issue_success(self):
        """Test should_increment_build_issue with build issue success."""
        result = should_increment_build_issue(
            issue_id="issue123",
            issue_version=1,
            incident_test_id=None,
            build_status="PASS",
        )
        assert result == ("issue123", 1, False)

    def test_should_increment_build_issue_with_unknown_issue(self):
        """Test should_increment_build_issue with unknown issue."""
        result = should_increment_build_issue(
            issue_id=None,
            issue_version=None,
            incident_test_id=None,
            build_status="FAIL",
        )
        assert result == (None, None, True)


class TestToIntOrDefault:
    def test_to_int_or_default_with_valid_int(self):
        """Test to_int_or_default with valid int."""
        result = to_int_or_default("123", 0)
        assert result == 123

    def test_to_int_or_default_with_invalid_string(self):
        """Test to_int_or_default with invalid string."""
        result = to_int_or_default("abc", 0)
        assert result == 0

    def test_to_int_or_default_with_none(self):
        """Test to_int_or_default with None."""
        result = to_int_or_default(None, 0)
        assert result == 0

    def test_to_int_or_default_with_float(self):
        """Test to_int_or_default with float string."""
        result = to_int_or_default("123.45", 0)
        assert result == 0

    def test_to_int_or_default_with_empty_string(self):
        """Test to_int_or_default with empty string."""
        result = to_int_or_default("", 0)
        assert result == 0

    def test_to_int_or_default_with_negative_number(self):
        """Test to_int_or_default with negative number."""
        result = to_int_or_default("-123", 0)
        assert result == -123


class TestFilterParamsInitialization:
    def test_init_with_process_body(self):
        """Test FilterParams initialization with process_body=True."""
        filter_params = FilterParams(FILTER_BODY_DATA, process_body=True)
        assert len(filter_params.filters) >= 3
        assert "test.status" in [f["field"] for f in filter_params.filters]

    def test_init_with_request(self):
        """Test FilterParams initialization with request."""
        filter_params = FilterParams(mock_request_with_filters(), process_body=False)
        assert len(filter_params.filters) == 2

    def test_add_filter(self):
        """Test add_filter method."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.add_filter("test.status", "PASS", "exact")

        assert len(filter_params.filters) == 1
        assert filter_params.filters[0]["field"] == "test.status"
        assert filter_params.filters[0]["value"] == "PASS"
        assert filter_params.filters[0]["comparison_op"] == "exact"


class TestFilterParamsValidation:
    def test_validate_comparison_op_valid(self):
        """Test validate_comparison_op with valid operator."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.validate_comparison_op("exact")

    def test_validate_comparison_op_invalid(self):
        """Test validate_comparison_op with invalid operator."""
        filter_params = FilterParams(mock_request(), process_body=False)
        with pytest.raises(InvalidComparisonOPError):
            filter_params.validate_comparison_op("invalid_op")


class TestFilterParamsOperations:
    def test_get_comparison_op_orm(self):
        """Test get_comparison_op with orm type."""
        filter_params = filter_params_with_exact_filter()
        result = filter_params.get_comparison_op(filter_params.filters[0], "orm")
        assert result == "exact"

    def test_get_comparison_op_raw(self):
        """Test get_comparison_op with raw type."""
        filter_params = filter_params_with_exact_filter()
        result = filter_params.get_comparison_op(filter_params.filters[0], "raw")
        assert result == "="

    def test_get_grouped_filters(self):
        """Test get_grouped_filters method."""
        filter_params = filter_params_with_filters()
        grouped = filter_params.get_grouped_filters()
        assert "test.status" in grouped
        assert grouped["test.status"]["value"] == ["PASS", "FAIL"]

    def test_get_grouped_filters_with_multiple_values_same_field(self):
        """Test get_grouped_filters with multiple values for same field (else case)."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filters = [
            {"field": "test.status", "value": "PASS", "comparison_op": "exact"},
            {"field": "test.status", "value": "FAIL", "comparison_op": "exact"},
            {"field": "test.status", "value": "SKIP", "comparison_op": "exact"},
        ]

        grouped = filter_params.get_grouped_filters()

        assert "test.status" in grouped
        assert grouped["test.status"]["value"] == ["PASS", "FAIL", "SKIP"]
        assert grouped["test.status"]["comparison_op"] == "exact"

    def test_get_grouped_filters_with_string_to_list_conversion(self):
        """Test get_grouped_filters with string to list conversion (elif case)."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filters = [
            {"field": "test.status", "value": "PASS", "comparison_op": "exact"},
            {"field": "test.status", "value": "FAIL", "comparison_op": "exact"},
        ]

        grouped = filter_params.get_grouped_filters()

        assert "test.status" in grouped
        assert grouped["test.status"]["value"] == ["PASS", "FAIL"]
        assert grouped["test.status"]["comparison_op"] == "exact"


class TestBuildFilters:
    def test_is_build_filtered_out_with_status_filter(self):
        """Test is_build_filtered_out with status filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterBuildStatus = {"FAIL"}
        result = filter_params.is_build_filtered_out(
            **{
                "duration": 100,
                "build_status": "PASS",
                "issue_id": "issue123",
                "issue_version": 1,
                "incident_test_id": None,
            }
        )
        assert result is True

    def test_is_build_filtered_out_with_duration_filter(self):
        """Test is_build_filtered_out with duration filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterBuildDurationMax = 100
        result = filter_params.is_build_filtered_out(
            duration=150,
            build_status="FAIL",
            issue_id="issue123",
            issue_version=1,
            incident_test_id=None,
        )
        assert result is True

    def test_is_build_filtered_out_with_origin_filter(self):
        """Test is_build_filtered_out with origin filter."""
        build_filter_data = {
            "duration": 100,
            "build_status": "FAIL",
            "issue_id": "issue123",
            "issue_version": 1,
            "incident_test_id": None,
            "build_origin": "origin2",
        }
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filter_build_origin = {"origin1"}
        result = filter_params.is_build_filtered_out(**build_filter_data)
        assert result is True


class TestRecordFilters:
    def test_is_record_filtered_out_with_hardware_filter(self):
        """Test is_record_filtered_out with hardware filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterHardware = {"hardware1"}
        result = filter_params.is_record_filtered_out(
            **{
                "hardwares": ["hardware2"],
                "architecture": "x86_64",
                "compiler": "gcc",
                "config_name": "defconfig",
            }
        )
        assert result is True

    def test_is_record_filtered_out_with_architecture_filter(self):
        """Test is_record_filtered_out with architecture filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterArchitecture = {"arm64"}
        result = filter_params.is_record_filtered_out(
            hardwares=["hardware1"],
            architecture="x86_64",
            compiler="gcc",
            config_name="defconfig",
        )
        assert result is True

    def test_is_record_filtered_out_with_compiler_filter(self):
        """Test is_record_filtered_out with compiler filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterCompiler = {"clang"}
        result = filter_params.is_record_filtered_out(
            hardwares=["hardware1"],
            architecture="x86_64",
            compiler="gcc",
            config_name="defconfig",
        )
        assert result is True

    def test_is_record_filtered_out_with_config_filter(self):
        """Test is_record_filtered_out with config filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterConfigs = {"allmodconfig"}
        result = filter_params.is_record_filtered_out(
            hardwares=["hardware1"],
            architecture="x86_64",
            compiler="gcc",
            config_name="defconfig",
        )
        assert result is True

    def test_is_record_filtered_out_with_no_filters_returns_false(self):
        """Test is_record_filtered_out with no filters returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        result = filter_params.is_record_filtered_out(
            hardwares=["hardware1"],
            architecture="x86_64",
            compiler="gcc",
            config_name="defconfig",
        )
        assert result is False

    def test_is_record_filtered_out_with_matching_hardware_returns_false(self):
        """Test is_record_filtered_out with matching hardware returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterHardware = {"hardware1"}
        result = filter_params.is_record_filtered_out(
            hardwares=["hardware1"],
            architecture="x86_64",
            compiler="gcc",
            config_name="defconfig",
        )
        assert result is False

    def test_is_record_filtered_out_with_matching_architecture_returns_false(self):
        """Test is_record_filtered_out with matching architecture returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterArchitecture = {"x86_64"}
        result = filter_params.is_record_filtered_out(
            hardwares=["hardware1"],
            architecture="x86_64",
            compiler="gcc",
            config_name="defconfig",
        )
        assert result is False

    def test_is_record_filtered_out_with_matching_compiler_returns_false(self):
        """Test is_record_filtered_out with matching compiler returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterCompiler = {"gcc"}
        result = filter_params.is_record_filtered_out(
            hardwares=["hardware1"],
            architecture="x86_64",
            compiler="gcc",
            config_name="defconfig",
        )
        assert result is False

    def test_is_record_filtered_out_with_matching_config_returns_false(self):
        """Test is_record_filtered_out with matching config returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterConfigs = {"defconfig"}
        result = filter_params.is_record_filtered_out(
            hardwares=["hardware1"],
            architecture="x86_64",
            compiler="gcc",
            config_name="defconfig",
        )
        assert result is False


class TestBootFilters:
    def test_is_boot_filtered_out_with_path_filter(self):
        """Test is_boot_filtered_out with path filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterBootPath = "boot.test"
        result = filter_params.is_boot_filtered_out(
            **BOOT_FILTER_DATA_SCENARIOS["base"]
        )
        assert result is True

    def test_is_boot_filtered_out_with_status_filter(self):
        """Test is_boot_filtered_out with status filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterBootStatus = {"PASS"}
        result = filter_params.is_boot_filtered_out(
            **BOOT_FILTER_DATA_SCENARIOS["with_status"]
        )
        assert result is True

    def test_is_boot_filtered_out_with_duration_filter(self):
        """Test is_boot_filtered_out with duration filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterBootDurationMax = 100
        result = filter_params.is_boot_filtered_out(
            **BOOT_FILTER_DATA_SCENARIOS["with_duration"]
        )
        assert result is True

    def test_is_boot_filtered_out_with_platform_filter(self):
        """Test is_boot_filtered_out with platform filter."""
        boot_filter_data = BOOT_FILTER_DATA_SCENARIOS["with_platform"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterPlatforms["boot"] = {"platform1"}
        result = filter_params.is_boot_filtered_out(**boot_filter_data)
        assert result is True

    def test_is_boot_filtered_out_with_origin_filter(self):
        """Test is_boot_filtered_out with origin filter."""
        boot_filter_data = BOOT_FILTER_DATA_SCENARIOS["with_origin"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filter_boot_origin = {"origin1"}
        result = filter_params.is_boot_filtered_out(**boot_filter_data)
        assert result is True

    def test_is_boot_filtered_out_with_no_filters_returns_false(self):
        """Test is_boot_filtered_out with no filters returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        result = filter_params.is_boot_filtered_out(
            **BOOT_FILTER_DATA_SCENARIOS["base"]
        )
        assert result is False

    def test_is_boot_filtered_out_with_matching_path_returns_false(self):
        """Test is_boot_filtered_out with matching path returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterBootPath = "boot.other"
        result = filter_params.is_boot_filtered_out(
            **BOOT_FILTER_DATA_SCENARIOS["base"]
        )
        assert result is False

    def test_is_boot_filtered_out_with_matching_status_returns_false(self):
        """Test is_boot_filtered_out with matching status returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterBootStatus = {"PASS"}
        result = filter_params.is_boot_filtered_out(
            **BOOT_FILTER_DATA_SCENARIOS["base"]
        )
        assert result is False

    def test_is_boot_filtered_out_with_matching_duration_max_returns_false(self):
        """Test is_boot_filtered_out with matching duration max returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterBootDurationMax = 150
        result = filter_params.is_boot_filtered_out(
            path="boot.test",
            status="PASS",
            duration=150,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is False

    def test_is_boot_filtered_out_with_matching_duration_min_returns_false(self):
        """Test is_boot_filtered_out with matching duration min returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterBootDurationMin = 50
        result = filter_params.is_boot_filtered_out(
            path="boot.test",
            status="PASS",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is False

    def test_is_boot_filtered_out_with_matching_platform_returns_false(self):
        """Test is_boot_filtered_out with matching platform returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterPlatforms["boot"] = {"platform1"}
        result = filter_params.is_boot_filtered_out(
            path="boot.test",
            status="PASS",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
            platform="platform1",
        )
        assert result is False

    def test_is_boot_filtered_out_with_matching_origin_returns_false(self):
        """Test is_boot_filtered_out with matching origin returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filter_boot_origin = {"origin1"}
        result = filter_params.is_boot_filtered_out(
            path="boot.test",
            status="PASS",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
            origin="origin1",
        )
        assert result is False


class TestTestFilters:
    def test_is_test_filtered_out_with_path_filter(self):
        """Test is_test_filtered_out with path filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterTestPath = "test.specific"
        result = filter_params.is_test_filtered_out(
            **{
                "path": "test.other",
                "status": "PASS",
                "duration": 100,
                "issue_id": "issue123",
                "issue_version": 1,
                "incident_test_id": "test123",
            }
        )
        assert result is True

    def test_is_test_filtered_out_with_status_filter(self):
        """Test is_test_filtered_out with status filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterTestStatus = {"PASS"}
        result = filter_params.is_test_filtered_out(
            path="test.specific",
            status="FAIL",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is True

    def test_is_test_filtered_out_with_duration_filter(self):
        """Test is_test_filtered_out with duration filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterTestDurationMax = 100
        result = filter_params.is_test_filtered_out(
            path="test.specific",
            status="PASS",
            duration=150,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is True

    def test_is_test_filtered_out_with_platform_filter(self):
        """Test is_test_filtered_out with platform filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterPlatforms["test"] = {"platform1"}
        result = filter_params.is_test_filtered_out(
            **{
                "path": "test.specific",
                "status": "PASS",
                "duration": 100,
                "issue_id": "issue123",
                "issue_version": 1,
                "incident_test_id": "test123",
                "platform": "platform2",
            }
        )
        assert result is True

    def test_is_test_filtered_out_with_origin_filter(self):
        """Test is_test_filtered_out with origin filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filter_test_origin = {"origin1"}
        result = filter_params.is_test_filtered_out(
            **{
                "path": "test.specific",
                "status": "PASS",
                "duration": 100,
                "issue_id": "issue123",
                "issue_version": 1,
                "incident_test_id": "test123",
                "origin": "origin2",
            }
        )
        assert result is True

    def test_is_test_filtered_out_with_no_filters_returns_false(self):
        """Test is_test_filtered_out with no filters returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        result = filter_params.is_test_filtered_out(
            path="test.specific",
            status="PASS",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is False

    def test_is_test_filtered_out_with_matching_path_returns_false(self):
        """Test is_test_filtered_out with matching path returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterTestPath = "test.specific"
        result = filter_params.is_test_filtered_out(
            path="test.specific",
            status="PASS",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is False

    def test_is_test_filtered_out_with_matching_status_returns_false(self):
        """Test is_test_filtered_out with matching status returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterTestStatus = {"PASS"}
        result = filter_params.is_test_filtered_out(
            path="test.specific",
            status="PASS",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is False

    def test_is_test_filtered_out_with_matching_duration_max_returns_false(self):
        """Test is_test_filtered_out with matching duration max returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterTestDurationMax = 150
        result = filter_params.is_test_filtered_out(
            path="test.specific",
            status="PASS",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is False

    def test_is_test_filtered_out_with_matching_duration_min_returns_false(self):
        """Test is_test_filtered_out with matching duration min returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterTestDurationMin = 50
        result = filter_params.is_test_filtered_out(
            path="test.specific",
            status="PASS",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
        )
        assert result is False

    def test_is_test_filtered_out_with_matching_platform_returns_false(self):
        """Test is_test_filtered_out with matching platform returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filterPlatforms["test"] = {"platform1"}
        result = filter_params.is_test_filtered_out(
            path="test.specific",
            status="PASS",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
            platform="platform1",
        )
        assert result is False

    def test_is_test_filtered_out_with_matching_origin_returns_false(self):
        """Test is_test_filtered_out with matching origin returns False."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filter_test_origin = {"origin1"}
        result = filter_params.is_test_filtered_out(
            path="test.specific",
            status="PASS",
            duration=100,
            issue_id="issue123",
            issue_version=1,
            incident_test_id="test123",
            origin="origin1",
        )
        assert result is False


class TestFilterHandlers:
    @patch("kernelCI_app.helpers.filters.log_message")
    def test_handle_issue_culprits_with_invalid_culprit(self, mock_log_message):
        """Test _handle_issue_culprits with invalid culprit."""
        invalid_culprit_filter_data = FILTER_OBJECTS["invalid_culprit"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_issue_culprits(invalid_culprit_filter_data)
        mock_log_message.assert_called_once()
        assert len(filter_params.filter_issue_culprits) == 0

    @patch("kernelCI_app.helpers.filters.log_message")
    def test_handle_issue_options_with_invalid_option(self, mock_log_message):
        """Test _handle_issue_options with invalid option."""
        invalid_option_filter_data = FILTER_OBJECTS["invalid_option"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_issue_options(invalid_option_filter_data)
        mock_log_message.assert_called_once()
        assert len(filter_params.filter_issue_options) == 0

    def test_handle_issues_with_uncategorized(self):
        """Test _handle_issues with uncategorized."""
        uncategorized_issue_filter_data = FILTER_OBJECTS["uncategorized_issue"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_issues(uncategorized_issue_filter_data)
        assert (UNCATEGORIZED_STRING, None) in filter_params.filterIssues["build"]

    def test_handle_issues_with_issue_tuple(self):
        """Test _handle_issues with issue tuple."""
        issue_tuple_filter_data = FILTER_OBJECTS["issue_tuple"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_issues(issue_tuple_filter_data)
        assert ("issue123", 1) in filter_params.filterIssues["build"]

    def test_handle_issues_with_issue_tuple_null_version(self):
        """Test _handle_issues with issue tuple null version."""
        issue_tuple_null_version_filter_data = FILTER_OBJECTS[
            "issue_tuple_null_version"
        ]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_issues(issue_tuple_null_version_filter_data)
        assert ("issue123", None) in filter_params.filterIssues["build"]

    def test_handle_platforms(self):
        """Test _handle_platforms."""
        platform_filter_data = FILTER_OBJECTS["platform"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_platforms(platform_filter_data)
        assert "x86_64" in filter_params.filterPlatforms["boot"]

    def test_handle_origins(self):
        """Test _handle_origins."""
        origin_filter_data = FILTER_OBJECTS["origin"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_origins(origin_filter_data)
        assert "origin1" in filter_params.filter_origins

    def test_handle_issue_categories(self):
        """Test _handle_issue_categories."""
        issue_categories_filter_data = FILTER_OBJECTS["issue_categories"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_issue_categories(issue_categories_filter_data)
        assert "category1" in filter_params.filter_issue_categories

    def test_handle_build_origin(self):
        """Test _handle_build_origin."""
        build_origin_filter_data = FILTER_OBJECTS["build_origin"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_build_origin(build_origin_filter_data)
        assert "origin1" in filter_params.filter_build_origin

    def test_handle_boot_origin(self):
        """Test _handle_boot_origin."""
        boot_origin_filter_data = FILTER_OBJECTS["boot_origin"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_boot_origin(boot_origin_filter_data)
        assert "origin1" in filter_params.filter_boot_origin

    def test_handle_test_origin(self):
        """Test _handle_test_origin."""
        test_origin_filter_data = FILTER_OBJECTS["test_origin"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_test_origin(test_origin_filter_data)
        assert "origin1" in filter_params.filter_test_origin

    def test_handle_boot_duration_lte(self):
        """Test _handle_boot_duration with lte operation."""
        boot_duration_lte_filter_data = FILTER_OBJECTS["boot_duration_lte"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_boot_duration(boot_duration_lte_filter_data)
        assert filter_params.filterBootDurationMax == 100
        assert filter_params.filterBootDurationMin is None

    def test_handle_boot_duration_gte(self):
        """Test _handle_boot_duration with gte operation."""
        boot_duration_gte_filter_data = FILTER_OBJECTS["boot_duration_gte"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_boot_duration(boot_duration_gte_filter_data)
        assert filter_params.filterBootDurationMin == 50
        assert filter_params.filterBootDurationMax is None

    def test_handle_test_duration_lte(self):
        """Test _handle_test_duration with lte operation."""
        test_duration_lte_filter_data = FILTER_OBJECTS["test_duration_lte"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_test_duration(test_duration_lte_filter_data)
        assert filter_params.filterTestDurationMax == 200
        assert filter_params.filterTestDurationMin is None

    def test_handle_test_duration_gte(self):
        """Test _handle_test_duration with gte operation."""
        test_duration_gte_filter_data = FILTER_OBJECTS["test_duration_gte"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_test_duration(test_duration_gte_filter_data)
        assert filter_params.filterTestDurationMin == 75
        assert filter_params.filterTestDurationMax is None

    def test_handle_build_duration_lte(self):
        """Test _handle_build_duration with lte operation."""
        build_duration_lte_filter_data = FILTER_OBJECTS["build_duration_lte"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_build_duration(build_duration_lte_filter_data)
        assert filter_params.filterBuildDurationMax == 300
        assert filter_params.filterBuildDurationMin is None

    def test_handle_build_duration_gte(self):
        """Test _handle_build_duration with gte operation."""
        build_duration_gte_filter_data = FILTER_OBJECTS["build_duration_gte"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_build_duration(build_duration_gte_filter_data)
        assert filter_params.filterBuildDurationMin == 150
        assert filter_params.filterBuildDurationMax is None

    def test_handle_path_boot_path(self):
        """Test _handle_path with boot.path field."""
        boot_path_filter_data = FILTER_OBJECTS["boot_path"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_path(boot_path_filter_data)
        assert filter_params.filterBootPath == "boot.test"
        assert filter_params.filterTestPath == ""

    def test_handle_path_test_path(self):
        """Test _handle_path with test.path field."""
        test_path_filter_data = FILTER_OBJECTS["test_path"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_path(test_path_filter_data)
        assert filter_params.filterTestPath == "test.specific"
        assert filter_params.filterBootPath == ""

    def test_handle_issues_with_issue_tuple_invalid_format(self):
        """Test _handle_issues with invalid issue tuple format."""
        invalid_issue_tuple_filter_data = FILTER_OBJECTS["invalid_issue_tuple"]
        filter_params = FilterParams(mock_request(), process_body=False)
        with pytest.raises(ValueError):
            filter_params._handle_issues(invalid_issue_tuple_filter_data)


class TestFilterProcessing:
    @patch("kernelCI_app.helpers.filters.HttpResponseBadRequest")
    @patch("kernelCI_app.helpers.filters.get_error_body_response")
    def test_process_filters_with_invalid_comparison_op_raises_exception(
        self, mock_get_error_body, mock_http_response
    ):
        """Test _process_filters with invalid comparison operator raises exception."""
        filter_params = filter_params_with_invalid_op()
        mock_response = "Mocked error response"
        mock_get_error_body.return_value = mock_response
        mock_http_response.return_value = "Mocked HttpResponseBadRequest"

        with patch.object(
            filter_params,
            "filter_handlers",
            {
                "test.status": MagicMock(
                    side_effect=InvalidComparisonOPError("Invalid operator")
                )
            },
        ):
            result = filter_params._process_filters()

        mock_get_error_body.assert_called_once_with("Invalid operator")
        mock_http_response.assert_called_once_with(mock_response)
        assert result == "Mocked HttpResponseBadRequest"

    def test_process_filters_with_valid_filters(self):
        """Test _process_filters with valid filters processes successfully."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.filters = [
            {"field": "test.status", "value": "PASS", "comparison_op": "exact"}
        ]
        mock_handler = MagicMock()
        filter_params.filter_handlers = {"test.status": mock_handler}

        result = filter_params._process_filters()

        assert result is None
        mock_handler.assert_called_once_with(filter_params.filters[0])


class TestFilterCreation:
    def test_create_filters_from_body_with_valid_filters(self):
        """Test create_filters_from_body with valid filters."""
        filter_params = FilterParams(FILTER_BODY_DATA, process_body=True)
        assert "PASS" in filter_params.filterTestStatus
        assert "FAIL" in filter_params.filterTestStatus
        assert filter_params.filterBootDurationMax == 100
        assert "PASS" in filter_params.filterBuildStatus
        assert filter_params.filterBootPath == "boot.test"
        assert filter_params.filterTestPath == "test.specific"
        assert ("issue123", 1) in filter_params.filterIssues["build"]
        assert "x86_64" in filter_params.filterPlatforms["boot"]
        assert "origin1" in filter_params.filter_origins
        assert "category1" in filter_params.filter_issue_categories
        assert "origin1" in filter_params.filter_build_origin
        assert "origin1" in filter_params.filter_boot_origin
        assert "origin1" in filter_params.filter_test_origin
        assert "x86_64" in filter_params.filterArchitecture
        assert "gcc" in filter_params.filterCompiler

    def test_create_filters_from_body_with_empty_filter(self):
        """Test create_filters_from_body with empty filter."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.create_filters_from_body({"filter": {}})
        assert len(filter_params.filters) == 0

    def test_create_filters_from_body_with_no_filter_key(self):
        """Test create_filters_from_body with no filter key."""
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params.create_filters_from_body({})
        assert len(filter_params.filters) == 0

    def test_create_filters_from_req_with_empty_request(self):
        """Test create_filters_from_req with empty request."""
        filter_params = FilterParams(mock_request(), process_body=False)
        assert len(filter_params.filters) == 0

    def test_create_filters_from_req_with_filters(self):
        """Test create_filters_from_req with filters."""
        filter_params = FilterParams(mock_request_with_filters(), process_body=False)
        assert len(filter_params.filters) == 2


class TestSpecificHandlers:
    def test_handle_boot_status(self):
        """Test _handle_boot_status method."""
        boot_status_filter_data = FILTER_OBJECTS["boot_status"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_boot_status(boot_status_filter_data)
        assert "PASS" in filter_params.filterBootStatus

    def test_handle_test_status(self):
        """Test _handle_test_status method."""
        test_status_filter_data = FILTER_OBJECTS["test_status"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_test_status(test_status_filter_data)
        assert "FAIL" in filter_params.filterTestStatus

    def test_handle_config_name(self):
        """Test _handle_config_name method."""
        config_name_filter_data = FILTER_OBJECTS["config_name"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_config_name(config_name_filter_data)
        assert "defconfig" in filter_params.filterConfigs

    def test_handle_compiler(self):
        """Test _handle_compiler method."""
        compiler_filter_data = FILTER_OBJECTS["compiler"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_compiler(compiler_filter_data)
        assert "gcc" in filter_params.filterCompiler

    def test_handle_architecture(self):
        """Test _handle_architecture method."""
        architecture_filter_data = FILTER_OBJECTS["architecture"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_architecture(architecture_filter_data)
        assert "x86_64" in filter_params.filterArchitecture

    def test_handle_hardware(self):
        """Test _handle_hardware method."""
        hardware_filter_data = FILTER_OBJECTS["hardware"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_hardware(hardware_filter_data)
        assert "hardware1" in filter_params.filterHardware

    def test_handle_build_status(self):
        """Test _handle_build_status method."""
        build_status_filter_data = FILTER_OBJECTS["build_status"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_build_status(build_status_filter_data)
        assert "PASS" in filter_params.filterBuildStatus

    @patch("kernelCI_app.helpers.filters.log_message")
    def test_handle_issue_culprits_with_valid_culprit(self, mock_log_message):
        """Test _handle_issue_culprits with valid culprit."""
        valid_culprit_filter_data = FILTER_OBJECTS["valid_culprit"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_issue_culprits(valid_culprit_filter_data)
        mock_log_message.assert_not_called()
        assert "code" in filter_params.filter_issue_culprits

    @patch("kernelCI_app.helpers.filters.log_message")
    def test_handle_issue_options_with_valid_option(self, mock_log_message):
        """Test _handle_issue_options with valid option."""
        valid_option_filter_data = FILTER_OBJECTS["valid_option"]
        filter_params = FilterParams(mock_request(), process_body=False)
        filter_params._handle_issue_options(valid_option_filter_data)
        mock_log_message.assert_not_called()
        assert "hasIncident" in filter_params.filter_issue_options


class TestRequestFilters:
    def test_create_filters_from_req_with_multiple_values(self):
        """Test create_filters_from_req with multiple values."""
        filter_params = FilterParams(
            mock_request_with_multiple_filters(), process_body=False
        )
        assert len(filter_params.filters) == 3

    def test_create_filters_from_req_with_string_like_filter(self):
        """Test create_filters_from_req with string-like filter."""
        filter_params = FilterParams(
            mock_request_with_string_filter(), process_body=False
        )
        assert len(filter_params.filters) == 1

    def test_create_filters_from_req_with_regex_match(self):
        """Test create_filters_from_req with regex match."""
        filter_params = FilterParams(
            mock_request_with_regex_filter(), process_body=False
        )
        assert len(filter_params.filters) == 1

    def test_create_filters_from_req_with_no_match(self):
        """Test create_filters_from_req with no match."""
        filter_params = FilterParams(
            mock_request_with_invalid_param(), process_body=False
        )
        assert len(filter_params.filters) == 0

    def test_create_filters_from_body_with_string_like_filter(self):
        """Test create_filters_from_body with string-like filter."""
        filter_params = FilterParams(
            {"filter": {"filter_test.path": "test.specific"}}, process_body=True
        )
        assert len(filter_params.filters) == 1

    def test_create_filters_from_body_with_exact_filter(self):
        """Test create_filters_from_body with exact filter."""
        filter_params = FilterParams(
            {"filter": {"filter_test.status": "PASS"}}, process_body=True
        )
        assert len(filter_params.filters) == 1
