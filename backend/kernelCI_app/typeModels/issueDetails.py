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


class IssuesBuildResponse(RootModel):
    root: List[IssueBuildItem]
