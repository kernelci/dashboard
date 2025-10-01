"""
Fixtures for filter tests.
"""

from unittest.mock import MagicMock
from django.http import HttpRequest, QueryDict
from kernelCI_app.constants.general import UNCATEGORIZED_STRING


def mock_request():
    """Mock HttpRequest for testing."""
    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict()
    return request


def mock_request_with_filters():
    """Mock HttpRequest with filter parameters."""
    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict("filter_test.status=PASS&filter_boot.duration_[lte]=100")
    return request


def mock_request_with_multiple_filters():
    """Mock HttpRequest with multiple filter parameters."""
    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict(
        "filter_test.status=PASS&filter_test.status=FAIL&filter_boot.duration_[lte]=100"
    )
    return request


def mock_request_with_string_filter():
    """Mock HttpRequest with string-like filter."""
    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict("filter_test.path=test.specific")
    return request


def mock_request_with_regex_filter():
    """Mock HttpRequest with regex filter."""
    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict("filter_boot.duration_[lte]=100")
    return request


def mock_request_with_invalid_param():
    """Mock HttpRequest with invalid parameter."""
    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict("invalid_param=value")
    return request


def filter_body_data():
    """Filter body data for testing."""
    return {
        "filter": {
            "filter_test.status": ["PASS", "FAIL"],
            "filter_boot.duration_[lte]": [100],
            "filter_build.status": ["PASS"],
            "filter_boot.path": "boot.test",
            "filter_test.path": "test.specific",
            "filter_build.issue": ["issue123,1"],
            "filter_boot.platform": ["x86_64"],
            "filter_origin": ["origin1"],
            "filter_issue.categories": ["category1"],
            "filter_build.origin": ["origin1"],
            "filter_boot.origin": ["origin1"],
            "filter_test.origin": ["origin1"],
            "filter_hardware": ["hardware1"],
            "filter_architecture": ["x86_64"],
            "filter_compiler": ["gcc"],
            "filter_config": ["defconfig"],
            "filter_issue.culprit": ["culprit1"],
            "filter_issue.options": ["option1"],
            "invalid_filter": ["should_be_ignored"],
        }
    }


def empty_filter_body():
    """Empty filter body data."""
    return {"filter": {}}


def no_filter_body():
    """Body without filter key."""
    return {}


def string_filter_body():
    """Body with string-like filter."""
    return {"filter": {"filter_test.path": "test.specific"}}


def exact_filter_body():
    """Body with exact filter."""
    return {"filter": {"filter_test.status": "PASS"}}


def issue_filters():
    """Issue filters for testing."""
    return {("issue123", 1), ("issue456", 2)}


def non_matching_issue_filters():
    """Non-matching issue filters for testing."""
    return {("issue456", 2), ("issue789", 3)}


def uncategorized_filters():
    """Uncategorized filters for testing."""
    return {UNCATEGORIZED_STRING}


def empty_filters():
    """Empty filters set."""
    return set()


def filter_data_with_uncategorized():
    """Filter data with uncategorized issue."""
    return {
        "issue_filter_data": UNCATEGORIZED_STRING,
        "issue_id": UNCATEGORIZED_STRING,
        "issue_version": None,
    }


def filter_data_with_tuple_match():
    """Filter data with tuple match."""
    return {
        "issue_filter_data": ("issue123", 1),
        "issue_id": "issue123",
        "issue_version": 1,
    }


def filter_data_with_tuple_no_match_id():
    """Filter data with tuple no match ID."""
    return {
        "issue_filter_data": ("issue123", 1),
        "issue_id": "issue456",
        "issue_version": 1,
    }


def filter_data_with_tuple_no_match_version():
    """Filter data with tuple no match version."""
    return {
        "issue_filter_data": ("issue123", 1),
        "issue_id": "issue123",
        "issue_version": 2,
    }


def filter_data_with_uncategorized_issue():
    """Filter data with uncategorized issue."""
    return {
        "issue_filter_data": UNCATEGORIZED_STRING,
        "issue_id": "issue123",
        "issue_version": 1,
    }


def build_filter_data():
    """Build filter data for testing."""
    return {
        "duration": 100,
        "build_status": "PASS",
        "issue_id": "issue123",
        "issue_version": 1,
        "incident_test_id": None,
    }


def build_filter_data_with_origin():
    """Build filter data with origin."""
    return {
        "duration": 100,
        "build_status": "FAIL",
        "issue_id": "issue123",
        "issue_version": 1,
        "incident_test_id": None,
        "build_origin": "origin2",
    }


def record_filter_data():
    """Record filter data for testing."""
    return {
        "hardwares": ["hardware2"],
        "architecture": "x86_64",
        "compiler": "gcc",
        "config_name": "defconfig",
    }


def boot_filter_data():
    """Boot filter data for testing."""
    return {
        "path": "boot.other",
        "status": "PASS",
        "duration": 100,
        "issue_id": "issue123",
        "issue_version": 1,
        "incident_test_id": "test123",
    }


def boot_filter_data_with_platform():
    """Boot filter data with platform."""
    return {
        "path": "boot.test",
        "status": "PASS",
        "duration": 100,
        "issue_id": "issue123",
        "issue_version": 1,
        "incident_test_id": "test123",
        "platform": "platform2",
    }


def boot_filter_data_with_origin():
    """Boot filter data with origin."""
    return {
        "path": "boot.test",
        "status": "PASS",
        "duration": 100,
        "issue_id": "issue123",
        "issue_version": 1,
        "incident_test_id": "test123",
        "origin": "origin2",
    }


def test_filter_data():
    """Test filter data for testing."""
    return {
        "path": "test.other",
        "status": "PASS",
        "duration": 100,
        "issue_id": "issue123",
        "issue_version": 1,
        "incident_test_id": "test123",
    }


def test_filter_data_with_platform():
    """Test filter data with platform."""
    return {
        "path": "test.specific",
        "status": "PASS",
        "duration": 100,
        "issue_id": "issue123",
        "issue_version": 1,
        "incident_test_id": "test123",
        "platform": "platform2",
    }


def test_filter_data_with_origin():
    """Test filter data with origin."""
    return {
        "path": "test.specific",
        "status": "PASS",
        "duration": 100,
        "issue_id": "issue123",
        "issue_version": 1,
        "incident_test_id": "test123",
        "origin": "origin2",
    }


def invalid_culprit_filter():
    """Invalid culprit filter data."""
    return {
        "field": "issue.culprit",
        "value": "invalid_culprit",
        "comparison_op": "exact",
    }


def invalid_option_filter():
    """Invalid option filter data."""
    return {
        "field": "issue.options",
        "value": "invalid_option",
        "comparison_op": "exact",
    }


def valid_culprit_filter():
    """Valid culprit filter data."""
    return {
        "field": "issue.culprit",
        "value": "code",
        "comparison_op": "exact",
    }


def valid_option_filter():
    """Valid option filter data."""
    return {
        "field": "issue.options",
        "value": "hasIncident",
        "comparison_op": "exact",
    }


def uncategorized_issue_filter():
    """Uncategorized issue filter data."""
    return {
        "field": "build.issue",
        "value": UNCATEGORIZED_STRING,
        "comparison_op": "exact",
    }


def issue_tuple_filter():
    """Issue tuple filter data."""
    return {
        "field": "build.issue",
        "value": "issue123,1",
        "comparison_op": "exact",
    }


def issue_tuple_null_version_filter():
    """Issue tuple null version filter data."""
    return {
        "field": "build.issue",
        "value": "issue123,null",
        "comparison_op": "exact",
    }


def invalid_issue_tuple_filter():
    """Invalid issue tuple filter data."""
    return {
        "field": "build.issue",
        "value": "invalid_format",
        "comparison_op": "exact",
    }


def platform_filter():
    """Platform filter data."""
    return {
        "field": "boot.platform",
        "value": "x86_64",
        "comparison_op": "exact",
    }


def origin_filter():
    """Origin filter data."""
    return {
        "field": "origin",
        "value": "origin1",
        "comparison_op": "exact",
    }


def issue_categories_filter():
    """Issue categories filter data."""
    return {
        "field": "issue.categories",
        "value": "category1",
        "comparison_op": "exact",
    }


def build_origin_filter():
    """Build origin filter data."""
    return {
        "field": "build.origin",
        "value": "origin1",
        "comparison_op": "exact",
    }


def boot_origin_filter():
    """Boot origin filter data."""
    return {
        "field": "boot.origin",
        "value": "origin1",
        "comparison_op": "exact",
    }


def test_origin_filter():
    """Test origin filter data."""
    return {
        "field": "test.origin",
        "value": "origin1",
        "comparison_op": "exact",
    }


def boot_duration_lte_filter():
    """Boot duration lte filter data."""
    return {
        "field": "boot.duration",
        "value": "100",
        "comparison_op": "lte",
    }


def boot_duration_gte_filter():
    """Boot duration gte filter data."""
    return {
        "field": "boot.duration",
        "value": "50",
        "comparison_op": "gte",
    }


def test_duration_lte_filter():
    """Test duration lte filter data."""
    return {
        "field": "test.duration",
        "value": "200",
        "comparison_op": "lte",
    }


def test_duration_gte_filter():
    """Test duration gte filter data."""
    return {
        "field": "test.duration",
        "value": "75",
        "comparison_op": "gte",
    }


def build_duration_lte_filter():
    """Build duration lte filter data."""
    return {
        "field": "build.duration",
        "value": ["300"],
        "comparison_op": "lte",
    }


def build_duration_gte_filter():
    """Build duration gte filter data."""
    return {
        "field": "build.duration",
        "value": ["150"],
        "comparison_op": "gte",
    }


def boot_path_filter():
    """Boot path filter data."""
    return {
        "field": "boot.path",
        "value": "boot.test",
        "comparison_op": "exact",
    }


def test_path_filter():
    """Test path filter data."""
    return {
        "field": "test.path",
        "value": "test.specific",
        "comparison_op": "exact",
    }


def boot_status_filter():
    """Boot status filter data."""
    return {
        "field": "boot.status",
        "value": "PASS",
        "comparison_op": "exact",
    }


def test_status_filter():
    """Test status filter data."""
    return {
        "field": "test.status",
        "value": "FAIL",
        "comparison_op": "exact",
    }


def config_name_filter():
    """Config name filter data."""
    return {
        "field": "config",
        "value": "defconfig",
        "comparison_op": "exact",
    }


def compiler_filter():
    """Compiler filter data."""
    return {
        "field": "compiler",
        "value": "gcc",
        "comparison_op": "exact",
    }


def architecture_filter():
    """Architecture filter data."""
    return {
        "field": "architecture",
        "value": "x86_64",
        "comparison_op": "exact",
    }


def hardware_filter():
    """Hardware filter data."""
    return {
        "field": "hardware",
        "value": "hardware1",
        "comparison_op": "exact",
    }


def build_status_filter():
    """Build status filter data."""
    return {
        "field": "build.status",
        "value": "PASS",
        "comparison_op": "exact",
    }


def invalid_comparison_op_filter():
    """Invalid comparison operator filter data."""
    return {
        "field": "test.status",
        "value": "PASS",
        "comparison_op": "invalid_op",
    }


def valid_comparison_op_filter():
    """Valid comparison operator filter data."""
    return {
        "field": "test.status",
        "value": "PASS",
        "comparison_op": "exact",
    }


def grouped_filters_data():
    """Grouped filters data for testing."""
    return [
        {"field": "test.status", "value": "PASS", "comparison_op": "exact"},
        {"field": "test.status", "value": "FAIL", "comparison_op": "exact"},
    ]


def filter_params_with_filters():
    """FilterParams with pre-configured filters."""
    from kernelCI_app.helpers.filters import FilterParams
    from django.http import QueryDict

    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict()
    filter_params = FilterParams(request, process_body=False)
    filter_params.filters = [
        {"field": "test.status", "value": "PASS", "comparison_op": "exact"},
        {"field": "test.status", "value": "FAIL", "comparison_op": "exact"},
    ]
    return filter_params


def filter_params_with_invalid_op():
    """FilterParams with invalid comparison operator."""
    from kernelCI_app.helpers.filters import FilterParams
    from django.http import QueryDict

    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict()
    filter_params = FilterParams(request, process_body=False)
    filter_params.filters = [
        {"field": "test.status", "value": "PASS", "comparison_op": "invalid_op"}
    ]
    return filter_params


def filter_params_with_exact_filter():
    """FilterParams with exact filter."""
    from kernelCI_app.helpers.filters import FilterParams
    from django.http import QueryDict

    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict()
    filter_params = FilterParams(request, process_body=False)
    filter_params.filters = [{"comparison_op": "exact"}]
    return filter_params
