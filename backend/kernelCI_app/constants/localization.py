# This file implements a rough start for localization,
# but it doesn't implement the entire localization system.

from enum import StrEnum, _simple_enum


# TODO: replace this enum with a proper localization system
@_simple_enum(StrEnum)
class ClientStrings:
    """Simple class for storing basis for internationalization strings"""

    TREE_BUILDS_NO_RESULTS = "No builds available for this tree/branch/commit"
    TREE_BOOTS_NO_RESULTS = "No boots available for this tree/branch/commit"
    TREE_NO_RESULTS = "No results available for this tree/branch/commit"
    TREE_TESTS_NO_RESULTS = "No tests available for this tree/branch/commit"
    TREE_COMMITS_HISTORY_NOT_FOUND = "History of tree commits not found"
    TREE_NOT_FOUND_IN_INTERVAL = "Tree not found in the given interval"
    TREE_REPORT_MIN_MAX_AGE = (
        "Minimum age can't be greater than or equal to the maximum age"
    )
    TEST_STATUS_HISTORY_NOT_FOUND = "Test status history not found"
    TEST_ISSUES_NOT_FOUND = "No issues were found for this test"
    TEST_NOT_FOUND = "Test not found"
    NO_TREES_FOUND = "No trees were found"
    PROXY_FETCH_FAILED = "Failed to fetch resource:"
    PROXY_INVALID_URL = "Invalid URL"
    PROXY_ERROR_FETCH = "Error fetching the resource"
    NO_ORIGIN_FOUND = "No origins found"
    LOG_TABLE_NOT_FOUND = "Table with id 'list' not found"
    LOG_TABLE_BODY_NOT_FOUND = "Table body not found"
    LOG_INVALID_TABLE_FORMAT = (
        "Invalid number of columns in table row (probably not a log website)"
    )
    LOG_NO_FILES_FOUND = "No log files found"
    ISSUE_NOT_FOUND = "Issue not found"
    NO_ISSUE_FOUND = "No issues found"
    INVALID_JSON_BODY = "Invalid body, request body must be a valid json string"
    ISSUE_EMPTY_LIST = "Invalid body, the issue list must not be empty"
    ISSUE_NO_EXTRA_DETAILS = (
        "No extra details found. Issue id has no incident or doesn't exist."
    )
    ISSUE_TESTS_NOT_FOUND = "No tests found for this issue"
    ISSUE_BUILDS_NOT_FOUND = "No builds found for this issue"
    NO_HARDWARE_FOUND = "No hardware found"
    HARDWARE_NOT_FOUND = "Hardware not found"
    HARDWARE_NO_COMMITS = "This hardware isn't associated with any commit"
    HARDWARE_TEST_NOT_FOUND = "No tests found for this hardware"
    INVALID_TIMESTAMP = (
        "startTimestampInSeconds and endTimestampInSeconds must be a Unix Timestamp"
    )
    HARDWARE_COMMIT_HISTORY_NOT_FOUND = "Commit history not found"
    HARDWARE_BUILDS_NOT_FOUND = "No builds found for this hardware"
    HARDWARE_BOOTS_NOT_FOUND = "No boots found for this hardware"
    BUILDS_TEST_NOT_FOUND = "No tests found for this build"
    BUILD_ISSUES_NOT_FOUND = "No issues found for this build"
    BUILD_DETAILS_NOT_FOUND = "Build not found"
    TREE_NOT_FOUND = "Tree not found."
    TREE_LATEST_DEFAULT_ORIGIN = "No origin was provided so it was defaulted to"


@_simple_enum(StrEnum)
class DocStrings:
    DEFAULT_START_TS_DESCRIPTION = "Interval start timestamp in seconds for the results"
    DEFAULT_END_TS_DESCRIPTION = "Interval end timestamp in seconds for the results"
    DEFAULT_GIT_BRANCH_DESCRIPTION = "Git branch name of the tree"
    DEFAULT_FILTER_DESCRIPTION = (
        "Optional filter dictionary for additional query parameters"
    )
    DEFAULT_INTERVAL_DESCRIPTION = "Interval in days for the listing"

    PROXY_URL_DESCRIPTION = "URL to the proxy"

    CHECKOUT_START_TIME_DESCRIPTION = "Start time of the checkout"
    COMMIT_HASH_PATH_DESCRIPTION = "Commit hash of the tree"
    TREE_NAME_PATH_DESCRIPTION = "Name of the tree"
    BUILD_ID_PATH_DESCRIPTION = "ID of the build"
    HARDWARE_ID_PATH_DESCRIPTION = (
        "ID of the hardware, as the name of the platform/compatible"
    )
    ISSUE_ID_PATH_DESCRIPTION = "ID of the issue"
    TEST_ID_PATH_DESCRIPTION = "ID of the test"

    LISTING_QUERY_ORIGIN_DESCRIPTION = "Origin filter"

    HARDWARE_DETAILS_ORIGIN_DESCRIPTION = "Origin of the tests of the hardware"
    HARDWARE_DETAILS_SEL_COMMITS_DESCRIPTION = (
        "Dictionary mapping tree names to selected commit hashes"
    )

    HARDWARE_LISTING_ORIGIN_DESCRIPTION = "Origin of the hardware"

    ISSUE_DETAILS_VERSION_DESCRIPTION = "Issue version"

    ISSUE_EXTRA_ID_LIST_DESCRIPTION = "List of issue ids"

    LOG_DOWNLOADER_URL_DESCRIPTION = "URL of the log to be downloaded"

    TREE_COMMIT_ORIGIN_DESCRIPTION = "Origin to retrieve the tree commits"
    TREE_COMMIT_GIT_URL_DESCRIPTION = "Git repository URL to retrieve the tree commits"
    TREE_COMMIT_GIT_BRANCH_DESCRIPTION = "Git branch name to retrieve the tree commits"
    TREE_COMMIT_START_TS_DESCRIPTION = "Start time filter in seconds for tree commits"
    TREE_COMMIT_END_TS_DESCRIPTION = "End time filter in seconds for tree commits"

    TREE_LATEST_TREE_NAME_DESCRIPTION = "Name of the tree to retrieve tree information"
    TREE_LATEST_GIT_BRANCH_DESCRIPTION = "Git branch name to retrieve tree information"
    TREE_LATEST_COMMIT_HASH_DESCRIPTION = "Commit hash to retrieve tree information"
    TREE_LATEST_ORIGIN_DESCRIPTION = "Origin filter to retrieve tree information"

    TREE_QUERY_ORIGIN_DESCRIPTION = "Origin of the tree"
    TREE_QUERY_GIT_URL_DESCRIPTION = "Git repository URL of the tree"

    STATUS_HISTORY_PATH_DESCRIPTION = "Test path filter"
    STATUS_HISTORY_ORIGIN_DESCRIPTION = "Origin filter to retrieve tests"
    STATUS_HISTORY_GIT_URL_DESCRIPTION = "Git repository URL to retrieve tests"
    STATUS_HISTORY_GIT_BRANCH_DESCRIPTION = "Git branch name to retrieve tests"
    STATUS_HISTORY_PLATFORM_DESCRIPTION = "Platform filter to retrieve tests"
    STATUS_HISTORY_CURRENT_TEST_START_DESCRIPTION = (
        "Test start time filter to retrieve tests prior to it"
    )
    STATUS_HISTORY_CONFIG_NAME_DESCRIPTION = "Config name filter to retrieve tests"
    STATUS_HISTORY_FIELD_TS_DESCRIPTION = (
        "Test timestamp filter to retrieve tests prior to it"
    )

    BUILD_STATUS_SUMMARY_DESCRIPTION = "Summary of build statuses"
    BOOT_STATUS_SUMMARY_DESCRIPTION = "Summary of boot test statuses"
    TEST_STATUS_SUMMARY_DESCRIPTION = "Summary of test statuses"

    REGRESSIONS_GROUP = "Regressions are grouped by hardware, config, and path."
    TREE_REPORT_PATH_DESCRIPTION = (
        "A list of test paths to query for. SQL Wildcard can be used."
    )
    TREE_REPORT_DASHBOARD_URL_DESCRIPTION = (
        "The dashboard url of this tree/branch/commit"
    )
    TREE_REPORT_POSSIBLE_REGRESSIONS_DESCRIPTION = (
        "History of tests that are possible regressions." + REGRESSIONS_GROUP
    )
    TREE_REPORT_FIXED_REGRESSIONS_DESCRIPTION = (
        "History of tests that are fixed regressions." + REGRESSIONS_GROUP
    )
    TREE_REPORT_UNSTABLE_TESTS_DESCRIPTION = (
        "History of tests that are unstable. " + REGRESSIONS_GROUP
    )
    TREE_REPORT_GROUP_SIZE_DESCRIPTION = (
        "Maximum number of entries to be retrieved in a test history."
    )
    TREE_REPORT_MAX_AGE = (
        "Maximum age for the queried checkout and related tests in hours"
    )
    TREE_REPORT_MIN_AGE = "Minimum age of the queried checkout in hours"
