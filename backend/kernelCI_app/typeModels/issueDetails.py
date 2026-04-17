from typing import List, Optional

from pydantic import BaseModel, BeforeValidator, Field, RootModel
from typing_extensions import Annotated

from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.common import make_default_validator
from kernelCI_app.typeModels.databases import (
    NULL_STATUS,
    Build__Architecture,
    Build__Compiler,
    Build__ConfigName,
    Build__Duration,
    Build__Id,
    Build__LogUrl,
    Build__Misc,
    Build__StartTime,
    Build__Status,
    Checkout__GitRepositoryBranch,
    Checkout__TreeName,
    Issue__Categories,
    Issue__Comment,
    Issue__CulpritCode,
    Issue__CulpritHarness,
    Issue__CulpritTool,
    Issue__Id,
    Issue__Misc,
    Issue__ReportSubject,
    Issue__ReportUrl,
    Issue__Version,
    Origin,
    StatusValues,
    Test__Duration,
    Test__EnvironmentCompatible,
    Test__EnvironmentMisc,
    Test__Id,
    Test__Path,
    Test__StartTime,
    Timestamp,
)
from kernelCI_app.typeModels.issues import ProcessedExtraDetailedIssues
from kernelCI_app.utils import validate_str_to_dict


class IssueDetailsPathParameters(BaseModel):
    issue_id: str


class IssueBuildItem(BaseModel):
    id: Build__Id
    architecture: Build__Architecture
    config_name: Build__ConfigName
    status: Annotated[
        Build__Status,
        Field(validation_alias="build_status"),
        make_default_validator(NULL_STATUS),
    ]
    start_time: Build__StartTime
    duration: Build__Duration
    compiler: Build__Compiler
    log_url: Build__LogUrl
    tree_name: Checkout__TreeName
    git_repository_branch: Checkout__GitRepositoryBranch
    misc: Build__Misc


class IssueTestItem(BaseModel):
    id: Test__Id
    status: Annotated[
        StatusValues,
        make_default_validator(NULL_STATUS),
    ]
    duration: Test__Duration
    path: Test__Path
    start_time: Test__StartTime
    environment_compatible: Test__EnvironmentCompatible
    environment_misc: Annotated[
        Test__EnvironmentMisc, BeforeValidator(validate_str_to_dict)
    ]
    tree_name: Checkout__TreeName
    git_repository_branch: Checkout__GitRepositoryBranch
    lab: Optional[str]


class IssueTestsResponse(RootModel):
    root: List[IssueTestItem]


class IssueBuildsResponse(RootModel):
    root: List[IssueBuildItem]


class IssueDetailsResponse(BaseModel):
    field_timestamp: Timestamp
    id: Issue__Id
    version: Issue__Version
    origin: Origin
    report_url: Issue__ReportUrl
    report_subject: Issue__ReportSubject
    culprit_code: Issue__CulpritCode
    culprit_tool: Issue__CulpritTool
    culprit_harness: Issue__CulpritHarness
    comment: Issue__Comment
    misc: Issue__Misc
    categories: Issue__Categories
    extra: Optional[ProcessedExtraDetailedIssues]


class IssueDetailsQueryParameters(BaseModel):
    version: Optional[int] = Field(
        None, description=DocStrings.ISSUE_DETAILS_VERSION_DESCRIPTION
    )
