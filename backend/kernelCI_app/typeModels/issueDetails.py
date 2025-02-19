from typing import List, Optional
from pydantic import BaseModel, RootModel, Field

from kernelCI_app.typeModels.databases import (
    Build__Id,
    Build__Architecture,
    Build__ConfigName,
    Build__Valid,
    Build__StartTime,
    Build__Duration,
    Build__Compiler,
    Build__LogUrl,
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


class IssueDetailsPathParameters(BaseModel):
    issue_id: str


class IssueBuildItem(BaseModel):
    id: Build__Id = Field(validation_alias="build__id")
    architecture: Build__Architecture = Field(validation_alias="build__architecture")
    config_name: Build__ConfigName = Field(validation_alias="build__config_name")
    valid: Build__Valid = Field(validation_alias="build__valid")
    start_time: Build__StartTime = Field(validation_alias="build__start_time")
    duration: Build__Duration = Field(validation_alias="build__duration")
    compiler: Build__Compiler = Field(validation_alias="build__compiler")
    log_url: Build__LogUrl = Field(validation_alias="build__log_url")
    tree_name: Checkout__TreeName = Field(validation_alias="build__checkout__tree_name")
    git_repository_branch: Checkout__GitRepositoryBranch = Field(
        validation_alias="build__checkout__git_repository_branch"
    )


class IssueTestItem(BaseModel):
    id: Test__Id = Field(validation_alias="test__id")
    status: Test__Status = Field(validation_alias="test__status")
    duration: Test__Duration = Field(validation_alias="test__duration")
    path: Test__Path = Field(validation_alias="test__path")
    start_time: Test__StartTime = Field(validation_alias="test__start_time")
    environment_compatible: Test__EnvironmentCompatible = Field(
        validation_alias="test__environment_compatible"
    )
    environment_misc: Test__EnvironmentMisc = Field(validation_alias="test__environment_misc")
    tree_name: Checkout__TreeName = Field(validation_alias="test__build__checkout__tree_name")
    git_repository_branch: Checkout__GitRepositoryBranch = Field(
        validation_alias="test__build__checkout__git_repository_branch"
    )


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
    extra: Optional[ProcessedExtraDetailedIssues]


class IssueDetailsQueryParameters(BaseModel):
    version: Optional[int] = None
