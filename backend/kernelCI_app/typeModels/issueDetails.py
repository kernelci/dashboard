from typing import List

from pydantic import BaseModel, RootModel

from kernelCI_app.typeModels.databases import (
    Build__Id,
    Build__Architecture,
    Build__ConfigName,
    Build__Valid,
    Build__StartTime,
    Build__Duration,
    Build__Compiler,
    Build__LogUrl,
    Test__Id,
    Test__Status,
    Test__Duration,
    Test__Path,
    Test__StartTime,
    Test__EnvironmentCompatible,
)


class IssueBuildItem(BaseModel):
    id: Build__Id
    architecture: Build__Architecture
    config_name: Build__ConfigName
    valid: Build__Valid
    start_time: Build__StartTime
    duration: Build__Duration
    compiler: Build__Compiler
    log_url: Build__LogUrl


class IssueTestItem(BaseModel):
    id: Test__Id
    status: Test__Status
    duration: Test__Duration
    path: Test__Path
    start_time: Test__StartTime
    environment_compatible: Test__EnvironmentCompatible


class IssuesTestsResponse(RootModel):
    root: List[IssueTestItem]


class IssuesBuildResponse(RootModel):
    root: List[IssueBuildItem]
