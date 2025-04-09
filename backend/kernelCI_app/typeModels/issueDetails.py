from typing import List, Optional
from typing_extensions import Annotated
from pydantic import BaseModel, BeforeValidator, RootModel, Field, field_validator
from kernelCI_app.helpers.build import build_status_map

from kernelCI_app.typeModels.databases import (
    Build__Id,
    Build__Architecture,
    Build__ConfigName,
    Build__Status,
    Build__StartTime,
    Build__Duration,
    Build__Compiler,
    Build__LogUrl,
    Issue__Categories,
    Issue__Id,
    Issue__Version,
    Issue__ReportUrl,
    Issue__ReportSubject,
    Issue__CulpritCode,
    Issue__CulpritTool,
    Issue__CulpritHarness,
    Issue__Comment,
    Issue__Misc,
    Origin,
    Test__Id,
    Test__Status,
    Test__Duration,
    Test__Path,
    Test__StartTime,
    Test__EnvironmentCompatible,
    Test__EnvironmentMisc,
    Timestamp,
    Checkout__TreeName,
    Checkout__GitRepositoryBranch,
)
from kernelCI_app.typeModels.issues import ProcessedExtraDetailedIssues

from kernelCI_app.utils import validate_str_to_dict


class IssueDetailsPathParameters(BaseModel):
    issue_id: str


class IssueBuildItem(BaseModel):
    id: Build__Id
    architecture: Build__Architecture
    config_name: Build__ConfigName
    status: Build__Status = Field(validation_alias="build_status")
    start_time: Build__StartTime
    duration: Build__Duration
    compiler: Build__Compiler
    log_url: Build__LogUrl
    tree_name: Checkout__TreeName
    git_repository_branch: Checkout__GitRepositoryBranch

    @field_validator("status", mode="before")
    @classmethod
    def valid_to_status(cls, value) -> str:
        if isinstance(value, bool) or value is None:
            return build_status_map(value)
        return value


class IssueTestItem(BaseModel):
    id: Test__Id
    status: Test__Status
    duration: Test__Duration
    path: Test__Path
    start_time: Test__StartTime
    environment_compatible: Test__EnvironmentCompatible
    environment_misc: Annotated[
        Test__EnvironmentMisc, BeforeValidator(validate_str_to_dict)
    ]
    tree_name: Checkout__TreeName
    git_repository_branch: Checkout__GitRepositoryBranch


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
    version: Optional[int] = None
