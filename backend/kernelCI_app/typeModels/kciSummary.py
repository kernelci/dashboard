from datetime import datetime
from typing import TypedDict
from typing_extensions import Annotated
from pydantic import BaseModel, Field

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.common import StatusCount, make_default_validator
from kernelCI_app.typeModels.databases import Test__Id, Test__StartTime, Test__Status
from kernelCI_app.typeModels.treeListing import TestStatusCount

DEFAULT_PATH_SEARCH = ["%"]
DEFAULT_GROUP_SIZE = 3


class KciSummaryQueryParameters(BaseModel):
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
            description=DocStrings.KCI_SUMMARY_PATH_DESCRIPTION,
        ),
        make_default_validator(DEFAULT_PATH_SEARCH),
    ]
    group_size: Annotated[
        int,
        Field(
            gt=0,
            default=DEFAULT_GROUP_SIZE,
            description=DocStrings.KCI_SUMMARY_GROUP_SIZE_DESCRIPTION,
        ),
        make_default_validator(DEFAULT_GROUP_SIZE),
    ]


class RegressionHistoryItem(TypedDict):
    id: Test__Id
    start_time: Test__StartTime
    status: Test__Status


type RegressionData = dict[str, dict[str, dict[str, list[RegressionHistoryItem]]]]
"""The history of tests is grouped by hardware, then config, then path."""


class KciSummaryResponse(BaseModel):
    dashboard_url: str = Field(
        description=DocStrings.KCI_SUMMARY_DASHBOARD_URL_DESCRIPTION
    )
    git_url: str = Field(description=DocStrings.TREE_QUERY_GIT_URL_DESCRIPTION)
    git_branch: str = Field(description=DocStrings.DEFAULT_GIT_BRANCH_DESCRIPTION)
    commit_hash: str = Field(description=DocStrings.COMMIT_HASH_PATH_DESCRIPTION)
    origin: str = Field(description=DocStrings.TREE_QUERY_ORIGIN_DESCRIPTION)
    checkout_start_time: datetime = Field(
        description=DocStrings.CHECKOUT_START_TIME_DESCRIPTION
    )
    build_status_summary: StatusCount = Field(
        description=DocStrings.BUILD_STATUS_SUMMARY_DESCRIPTION,
    )
    boot_status_summary: TestStatusCount = Field(
        description=DocStrings.BOOT_STATUS_SUMMARY_DESCRIPTION
    )
    test_status_summary: TestStatusCount = Field(
        description=DocStrings.TEST_STATUS_SUMMARY_DESCRIPTION
    )
    possible_regressions: RegressionData = Field(
        description=DocStrings.KCI_SUMMARY_POSSIBLE_REGRESSIONS_DESCRIPTION,
    )
    fixed_regressions: RegressionData = Field(
        description=DocStrings.KCI_SUMMARY_FIXED_REGRESSIONS_DESCRIPTION
    )
    unstable_tests: RegressionData = Field(
        description=DocStrings.KCI_SUMMARY_UNSTABLE_TESTS_DESCRIPTION,
    )
