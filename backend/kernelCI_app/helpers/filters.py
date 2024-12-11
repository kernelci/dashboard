from typing import Optional
from kernelCI_app.utils import UNKNOWN_STRING


def is_build_invalid(build_valid: Optional[bool]) -> bool:
    return build_valid is None or build_valid is False


def is_known_issue(issue_id: Optional[str]) -> bool:
    return issue_id is not None and issue_id is not UNKNOWN_STRING


def is_issue_from_test(incident_test_id: Optional[str], is_known_issue: bool) -> bool:
    return incident_test_id is not None or not is_known_issue


def is_issue_filtered_out(issue_id: Optional[str], issue_filters: set) -> bool:
    return issue_id not in issue_filters


def should_filter_test_issue(
    issue_filters: set, issue_id: Optional[str], incident_test_id: Optional[str]
) -> bool:
    has_issue_filter = len(issue_filters) > 0

    is_known_issue_result = is_known_issue(issue_id)
    is_issue_from_tests_result = is_issue_from_test(
        incident_test_id, is_known_issue_result
    )

    is_issue_filtered_out_result = is_issue_filtered_out(issue_id, issue_filters)

    return (
        has_issue_filter and is_issue_from_tests_result and is_issue_filtered_out_result
    )


def should_increment_test_issue(
    issue_id: Optional[str], incident_test_id: Optional[str]
) -> bool:
    is_known_issue_result = is_known_issue(issue_id=issue_id)
    is_exclusively_build_issue = is_known_issue_result and incident_test_id is None
    if is_exclusively_build_issue:
        issue_id = UNKNOWN_STRING

    is_unknown_issue = issue_id is UNKNOWN_STRING
    is_known_test_issue = incident_test_id is not None
    is_issue_from_test = is_known_test_issue or is_unknown_issue

    return is_issue_from_test
