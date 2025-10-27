"""
Fixtures for filter tests.
"""

from unittest.mock import MagicMock
from django.http import HttpRequest, QueryDict
from kernelCI_app.constants.general import UNCATEGORIZED_STRING
from kernelCI_app.helpers.filters import FilterParams


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
    """Mock HttpRequest with multiple parameters of the same field."""
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


# Filter body data for testing
FILTER_BODY_DATA = {
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


# Matching issue filters for testing
MATCHING_ISSUE_FILTERS = {("issue123", 1), ("issue456", 2)}


FILTER_DATA_SCENARIOS = {
    "uncategorized": {
        "issue_filter_data": UNCATEGORIZED_STRING,
        "issue_id": UNCATEGORIZED_STRING,
        "issue_version": None,
    },
    "tuple_match": {
        "issue_filter_data": ("issue123", 1),
        "issue_id": "issue123",
        "issue_version": 1,
    },
    "tuple_no_match_id": {
        "issue_filter_data": ("issue123", 1),
        "issue_id": "issue456",
        "issue_version": 1,
    },
    "tuple_no_match_version": {
        "issue_filter_data": ("issue123", 1),
        "issue_id": "issue123",
        "issue_version": 2,
    },
    "uncategorized_issue": {
        "issue_filter_data": UNCATEGORIZED_STRING,
        "issue_id": "issue123",
        "issue_version": 1,
    },
}


def make_boot_filter_data(**overrides):
    base = {
        "path": "boot.other",
        "status": "PASS",
        "duration": 100,
        "issue_id": "issue123",
        "issue_version": 1,
        "incident_test_id": "test123",
    }
    base.update(overrides)
    return base


BOOT_FILTER_DATA_SCENARIOS = {
    "base": make_boot_filter_data(),
    "with_platform": make_boot_filter_data(platform="platform2"),
    "with_origin": make_boot_filter_data(origin="origin2"),
    "with_status": make_boot_filter_data(status="FAIL"),
    "with_duration": make_boot_filter_data(duration=150),
}


def make_filter_object(field, value, comparison_op="exact"):
    return {
        "field": field,
        "value": value,
        "comparison_op": comparison_op,
    }


FILTER_OBJECTS = {
    "invalid_culprit": make_filter_object("issue.culprit", "invalid_culprit"),
    "invalid_option": make_filter_object("issue.options", "invalid_option"),
    "valid_culprit": make_filter_object("issue.culprit", "code"),
    "valid_option": make_filter_object("issue.options", "hasIncident"),
    "uncategorized_issue": make_filter_object("build.issue", UNCATEGORIZED_STRING),
    "issue_tuple": make_filter_object("build.issue", "issue123,1"),
    "issue_tuple_null_version": make_filter_object("build.issue", "issue123,null"),
    "invalid_issue_tuple": make_filter_object("build.issue", "invalid_format"),
    "platform": make_filter_object("boot.platform", "x86_64"),
    "origin": make_filter_object("origin", "origin1"),
    "issue_categories": make_filter_object("issue.categories", "category1"),
    "build_origin": make_filter_object("build.origin", "origin1"),
    "boot_origin": make_filter_object("boot.origin", "origin1"),
    "test_origin": make_filter_object("test.origin", "origin1"),
    "boot_duration_lte": make_filter_object("boot.duration", "100", "lte"),
    "boot_duration_gte": make_filter_object("boot.duration", "50", "gte"),
    "test_duration_lte": make_filter_object("test.duration", "200", "lte"),
    "test_duration_gte": make_filter_object("test.duration", "75", "gte"),
    "build_duration_lte": make_filter_object("build.duration", ["300"], "lte"),
    "build_duration_gte": make_filter_object("build.duration", ["150"], "gte"),
    "boot_path": make_filter_object("boot.path", "boot.test"),
    "test_path": make_filter_object("test.path", "test.specific"),
    "boot_status": make_filter_object("boot.status", "PASS"),
    "test_status": make_filter_object("test.status", "FAIL"),
    "config_name": make_filter_object("config", "defconfig"),
    "compiler": make_filter_object("compiler", "gcc"),
    "architecture": make_filter_object("architecture", "x86_64"),
    "hardware": make_filter_object("hardware", "hardware1"),
    "build_status": make_filter_object("build.status", "PASS"),
    "invalid_comparison_op": make_filter_object("test.status", "PASS", "invalid_op"),
    "valid_comparison_op": make_filter_object("test.status", "PASS", "exact"),
}


def filter_params_with_filters():
    """FilterParams with pre-configured filters."""
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
    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict()
    filter_params = FilterParams(request, process_body=False)
    filter_params.filters = [
        {"field": "test.status", "value": "PASS", "comparison_op": "invalid_op"}
    ]
    return filter_params


def filter_params_with_exact_filter():
    """FilterParams with exact filter."""
    request = MagicMock(spec=HttpRequest)
    request.GET = QueryDict()
    filter_params = FilterParams(request, process_body=False)
    filter_params.filters = [{"comparison_op": "exact"}]
    return filter_params
