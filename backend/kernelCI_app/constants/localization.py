# This file implements a rough start for localization,
# but it doesn't implement the entire localization system.

from enum import StrEnum, _simple_enum


# TODO: replace this enum with a proper localization system
@_simple_enum(StrEnum)
class ClientStrings:
    """Simple class for storing basis for internationalization strings"""

    TREE_BUILDS_NOT_FOUND = "No builds available for this tree/branch/commit"
    TREE_BOOTS_NOT_FOUND = "No boots available for this tree/branch/commit"
    TREE_NOT_FOUND = "No results available for this tree/branch/commit"
    TREE_TESTS_NOT_FOUND = "No tests available for this tree/branch/commit"
    TREE_COMMITS_HISTORY_NOT_FOUND = "History of tree commits not found"
    TREE_STATUS_HISTORY_NOT_FOUND = "Test status history not found"
    TEST_NO_ISSUE_FOUND = "No issues were found for this test"
    TEST_NOT_FOUND = "Test not found"
    PROXY_FETCH_FAILED  = "Failed to fetch resource:"
    PROXY_INVALID_URL = "Invalid URL"
    PROXY_ERROR_FETCH = "Error fetching the resource"
    ORIGIN_NOT_FOUND = "No origins found"
    LOG_TABLE_NOT_FOUND = "Table with id 'list' not found"
    LOG_TABLE_BODY_NOT_FOUND = "Table body not found"
    LOG_INVALID_TABLE_FORMAT = "Invalid number of columns in table row (probably not a log website)"
    LOG_NO_FILES_FOUND = "No log files found"    
    ISSUE_NOT_FOUND = "No issues found"
    ISSUE_INVALID_JSON = "Invalid body, request body must be a valid json string"
    ISSUE_EMPTY_LIST = "Invalid body, the issue list must not be empty"
    ISSUE_NO_EXTRA_DETAILS = "No extra details found"
    ISSUE_TEST_NOT_FOUND = "No tests found for this issue"
    ISSUE_DETAILS_BUILD_NOT_FOUND = "No builds found for this issue"
    HARDWARE_NOT_FOUND = "No hardwares found"
    HARDWARE_INVALID_JSON = "Invalid body, request body must be a valid json string"
    HARDWARE_INVALID_TIMESTAMP = "startTimeStamp and endTimeStamp must be a Unix Timestamp"
    HARDWARE_NO_COMMITS = "This hardware isn't associated with any commit"
    HARDWARE_TEST_NOT_FOUND = "No tests found for this hardware"
    HARDWARE_COMMMIT_HISTORY_INVALID_TIMESTAMP = "startTimestampInSeconds and endTimestampInSeconds must be a Unix Timestamp"
    HARDWARE_COMMIT_HISTORY_NOT_FOUND = "Commit history not found"
    HARDWARE_BUILDS_NOT_FOUND = "No builds found for this hardware"
    HARDWARE_BOOTS_NOT_FOUND = "No boots found for this hardware"
    BUILDS_TESTS_NOT_FOUND = "No tests found for this build"
    BUILD_ISSUES_NOT_FOUND = "No issues were found for this build"
    BUILD_DETAILS_NOT_FOUND = "Build not found"
    TREE_LATEST_NOT_FOUND = "Tree not found."
    TREE_LATEST_DEFAULT_ORIGIN = " No origin was provided so it was defaulted to"    