from datetime import datetime
from typing import TypedDict
from kernelCI_app.typeModels.issues import CheckoutIssue
from typing_extensions import Annotated
from pydantic import BaseModel, Field

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.common import StatusCount, make_default_validator
from kernelCI_app.typeModels.databases import Test__Id, Test__StartTime, Test__Status
from kernelCI_app.typeModels.treeListing import TestStatusCount

DEFAULT_PATH_SEARCH = ["%"]
DEFAULT_GROUP_SIZE = 3
DEFAULT_MAX_AGE_HOURS = 24
DEFAULT_MIN_AGE_HOURS = 0
LIMIT_MAX_AGE_HOURS = 720  # 30 days


class TreeReportQueryParameters(BaseModel):
    origin: Annotated[
        str,
        Field(
            default=DEFAULT_ORIGIN,
            description=DocStrings.TREE_QUERY_ORIGIN_DESCRIPTION,
        ),
        make_default_validator(DEFAULT_ORIGIN),
    ]
    git_branch: Annotated[
        str,
        Field(description=DocStrings.DEFAULT_GIT_BRANCH_DESCRIPTION),
    ]
    git_url: Annotated[
        str,
        Field(description=DocStrings.TREE_QUERY_GIT_URL_DESCRIPTION),
    ]
    path: Annotated[
        list[str],
        Field(
            default=DEFAULT_PATH_SEARCH,
            description=DocStrings.TREE_REPORT_PATH_DESCRIPTION,
        ),
        make_default_validator(DEFAULT_PATH_SEARCH),
    ]
    group_size: Annotated[
        int,
        Field(
            gt=1,
            default=DEFAULT_GROUP_SIZE,
            description=DocStrings.TREE_REPORT_GROUP_SIZE_DESCRIPTION,
        ),
        make_default_validator(DEFAULT_GROUP_SIZE),
    ]
    min_age_in_hours: Annotated[
        int,
        Field(
            default=DEFAULT_MIN_AGE_HOURS,
            gte=0,
            description=DocStrings.TREE_REPORT_MIN_AGE,
        ),
        make_default_validator(DEFAULT_MIN_AGE_HOURS),
    ]
    max_age_in_hours: Annotated[
        int,
        Field(
            default=DEFAULT_MAX_AGE_HOURS,
            gt=0,
            le=LIMIT_MAX_AGE_HOURS,
            description=DocStrings.TREE_REPORT_MAX_AGE,
        ),
        make_default_validator(DEFAULT_MAX_AGE_HOURS),
    ]


class RegressionHistoryItem(TypedDict):
    id: Test__Id
    start_time: Test__StartTime
    status: Test__Status


type RegressionData = dict[str, dict[str, dict[str, list[RegressionHistoryItem]]]]
"""The history of tests is grouped by hardware, then config, then path."""


class TreeReportIssues(BaseModel):
    builds: Annotated[
        list[CheckoutIssue],
        Field(description=DocStrings.TREE_REPORT_BUILD_DESCRIPTION),
    ]


class TreeReportResponse(BaseModel):
    dashboard_url: Annotated[
        str, Field(description=DocStrings.TREE_REPORT_DASHBOARD_URL_DESCRIPTION)
    ]
    git_url: Annotated[
        str, Field(description=DocStrings.TREE_QUERY_GIT_URL_DESCRIPTION)
    ]
    git_branch: Annotated[
        str, Field(description=DocStrings.DEFAULT_GIT_BRANCH_DESCRIPTION)
    ]
    commit_hash: Annotated[
        str, Field(description=DocStrings.COMMIT_HASH_PATH_DESCRIPTION)
    ]
    origin: Annotated[str, Field(description=DocStrings.TREE_QUERY_ORIGIN_DESCRIPTION)]
    checkout_start_time: Annotated[
        datetime, Field(description=DocStrings.CHECKOUT_START_TIME_DESCRIPTION)
    ]
    build_status_summary: Annotated[
        StatusCount, Field(description=DocStrings.BUILD_STATUS_SUMMARY_DESCRIPTION)
    ]
    boot_status_summary: Annotated[
        TestStatusCount, Field(description=DocStrings.BOOT_STATUS_SUMMARY_DESCRIPTION)
    ]
    test_status_summary: Annotated[
        TestStatusCount, Field(description=DocStrings.TEST_STATUS_SUMMARY_DESCRIPTION)
    ]
    possible_regressions: Annotated[
        RegressionData,
        Field(description=DocStrings.TREE_REPORT_POSSIBLE_REGRESSIONS_DESCRIPTION),
    ]
    fixed_regressions: Annotated[
        RegressionData,
        Field(description=DocStrings.TREE_REPORT_FIXED_REGRESSIONS_DESCRIPTION),
    ]
    unstable_tests: Annotated[
        RegressionData,
        Field(description=DocStrings.TREE_REPORT_UNSTABLE_TESTS_DESCRIPTION),
    ]
    issues: Annotated[
        TreeReportIssues,
        Field(description=DocStrings.TREE_REPORT_ISSUES_DESCRIPTION),
    ]
