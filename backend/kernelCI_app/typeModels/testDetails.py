from typing import Literal, Optional
from typing_extensions import Annotated
from pydantic import BaseModel, BeforeValidator, Field, PositiveInt
from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings

from kernelCI_app.typeModels.databases import (
    Origin,
    Test__Id,
    Build__Id,
    Test__Status,
    Test__Path,
    Test__LogExcerpt,
    Test__LogUrl,
    Test__Misc,
    Test__EnvironmentMisc,
    Test__StartTime,
    Test__EnvironmentCompatible,
    Test__OutputFiles,
    Test__InputFiles,
    Build__Compiler,
    Build__Architecture,
    Build__ConfigName,
    Checkout__GitCommitHash,
    Checkout__GitRepositoryBranch,
    Checkout__GitRepositoryUrl,
    Checkout__GitCommitTags,
    Checkout__TreeName,
    Timestamp,
)
from kernelCI_app.utils import validate_str_to_dict


class TestDetailsResponse(BaseModel):
    field_timestamp: Timestamp = Field(validation_alias="_timestamp")
    id: Test__Id
    build_id: Build__Id
    status: Test__Status
    path: Test__Path
    log_excerpt: Test__LogExcerpt
    log_url: Test__LogUrl
    misc: Annotated[Test__Misc, BeforeValidator(validate_str_to_dict)]
    environment_misc: Annotated[
        Test__EnvironmentMisc, BeforeValidator(validate_str_to_dict)
    ]
    start_time: Test__StartTime
    environment_compatible: Test__EnvironmentCompatible
    output_files: Annotated[Test__OutputFiles, BeforeValidator(validate_str_to_dict)]
    input_files: Annotated[Test__InputFiles, BeforeValidator(validate_str_to_dict)]
    compiler: Build__Compiler
    architecture: Build__Architecture
    config_name: Build__ConfigName
    git_commit_hash: Checkout__GitCommitHash
    git_repository_branch: Checkout__GitRepositoryBranch
    git_repository_url: Checkout__GitRepositoryUrl
    git_commit_tags: Checkout__GitCommitTags
    tree_name: Checkout__TreeName
    origin: Optional[Origin]


type PossibleRegressionType = Literal["regression", "fixed", "unstable", "pass", "fail"]


class TestStatusHistoryItem(BaseModel):
    start_time: Test__StartTime
    id: Test__Id
    status: Test__Status
    git_commit_hash: Checkout__GitCommitHash = Field(
        validation_alias="build__checkout__git_commit_hash"
    )


class TestStatusHistoryResponse(BaseModel):
    status_history: list[TestStatusHistoryItem]
    regression_type: PossibleRegressionType


class TestStatusSeriesResponse(BaseModel):
    status_history: list[TestStatusHistoryItem]
    regression_type: PossibleRegressionType
    test_series: str
    build_series: str


class TestStatusSeriesRequest(BaseModel):
    path: Annotated[
        Optional[str],
        Field(None, description=DocStrings.STATUS_HISTORY_PATH_DESCRIPTION),
    ]
    platform: Annotated[
        Optional[str],
        Field(None, description=DocStrings.STATUS_HISTORY_PLATFORM_DESCRIPTION),
    ]
    origin: Annotated[
        Optional[str],
        Field(DEFAULT_ORIGIN, description=DocStrings.STATUS_HISTORY_ORIGIN_DESCRIPTION),
    ]
    config_name: Annotated[
        Optional[str],
        Field(None, description=DocStrings.STATUS_HISTORY_CONFIG_NAME_DESCRIPTION),
    ]
    architecture: Annotated[
        Optional[str],
        Field(None, description=DocStrings.SERIES_ARCHITECTURE_DESCRIPTION),
    ]
    compiler: Annotated[
        Optional[str],
        Field(None, description=DocStrings.SERIES_COMPILER_DESCRIPTION),
    ]
    group_size: Annotated[
        PositiveInt,
        Field(
            default=10,
            description=DocStrings.STATUS_HISTORY_GROUP_SIZE_DESCRIPTION,
        ),
    ]


class TestStatusHistoryRequest(BaseModel):
    path: Annotated[
        str, Field(None, description=DocStrings.STATUS_HISTORY_PATH_DESCRIPTION)
    ]
    origin: Annotated[
        Optional[str],
        Field(DEFAULT_ORIGIN, description=DocStrings.STATUS_HISTORY_ORIGIN_DESCRIPTION),
    ]
    git_repository_url: Annotated[
        Optional[str],
        Field(None, description=DocStrings.STATUS_HISTORY_GIT_URL_DESCRIPTION),
    ]
    git_repository_branch: Annotated[
        Optional[str],
        Field(None, description=DocStrings.STATUS_HISTORY_GIT_BRANCH_DESCRIPTION),
    ]
    platform: Annotated[
        Optional[str],
        Field(None, description=DocStrings.STATUS_HISTORY_PLATFORM_DESCRIPTION),
    ]
    current_test_start_time: Annotated[
        Test__StartTime,
        Field(
            None, description=DocStrings.STATUS_HISTORY_CURRENT_TEST_START_DESCRIPTION
        ),
    ]
    config_name: Annotated[
        Optional[str],
        Field(None, description=DocStrings.STATUS_HISTORY_CONFIG_NAME_DESCRIPTION),
    ]
    field_timestamp: Annotated[
        Timestamp,
        Field(None, description=DocStrings.STATUS_HISTORY_FIELD_TS_DESCRIPTION),
    ]
    group_size: Annotated[
        PositiveInt,
        Field(
            default=10,
            description=DocStrings.STATUS_HISTORY_GROUP_SIZE_DESCRIPTION,
        ),
    ]
