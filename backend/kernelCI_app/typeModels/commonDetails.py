import json
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Union, Tuple, Any

from pydantic import BaseModel, field_validator, Field
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.issues import Issue
from kernelCI_app.typeModels.databases import (
    EnvironmentMisc,
    Build__Id,
    Build__Architecture,
    Build__ConfigName,
    Build__Misc,
    Build__ConfigUrl,
    Build__Compiler,
    Build__Status,
    Build__LogUrl,
    Build__StartTime,
    Build__Duration,
    Checkout__GitRepositoryUrl,
    Checkout__GitRepositoryBranch,
    Origin,
)
from kernelCI_app.helpers.build import build_status_map


class TestArchSummaryItem(BaseModel):
    arch: str
    compiler: str
    status: StatusCount


class BuildArchitectures(StatusCount):
    compilers: Optional[List[str]] = []


class TestHistoryItem(BaseModel):
    id: str
    origin: Origin
    status: Optional[str]
    duration: Optional[Union[int, float]]
    path: Optional[str]
    start_time: Optional[Union[datetime, str]]
    environment_compatible: Optional[Union[str, List[str]]]
    config: Optional[str]
    log_url: Optional[str]
    architecture: Optional[str]
    compiler: Optional[str]
    environment_misc: Optional[EnvironmentMisc]


class BuildHistoryItem(BaseModel):
    id: Build__Id
    origin: Origin
    architecture: Build__Architecture
    config_name: Build__ConfigName
    misc: Build__Misc
    config_url: Build__ConfigUrl
    compiler: Build__Compiler
    status: Build__Status = Field(validation_alias="valid")
    duration: Build__Duration
    log_url: Build__LogUrl
    start_time: Build__StartTime
    git_repository_url: Checkout__GitRepositoryUrl
    git_repository_branch: Checkout__GitRepositoryBranch

    @field_validator("misc", mode="before")
    @classmethod
    def to_dict(cls, value: Any) -> Any:
        if isinstance(value, str):
            return json.loads(value)
        elif isinstance(value, dict):
            return value
        elif value is None:
            return None
        else:
            log_message(f"Invalid misc for BuildHistoryItem;\nType: {type(value)}")

    @field_validator("status", mode="before")
    @classmethod
    def valid_to_status(cls, value: Any) -> str:
        if isinstance(value, bool) or value is None:
            return build_status_map(value)
        return value


class TestSummary(BaseModel):
    status: StatusCount
    origins: dict[str, StatusCount]
    architectures: List[TestArchSummaryItem]
    configs: Dict[str, StatusCount]
    issues: List[Issue]
    unknown_issues: int
    fail_reasons: defaultdict[str, int]
    failed_platforms: Set
    environment_compatible: Optional[Dict] = None
    environment_misc: Optional[Dict] = None
    platforms: Optional[Dict[str, StatusCount]] = None


class BuildSummary(BaseModel):
    status: StatusCount
    origins: dict[str, StatusCount]
    architectures: Dict[str, BuildArchitectures]
    configs: Dict[str, StatusCount]
    issues: List[Issue]
    unknown_issues: int


class Summary(BaseModel):
    builds: BuildSummary
    boots: TestSummary
    tests: TestSummary


class GlobalFilters(BaseModel):
    configs: List[str]
    architectures: List[str]
    compilers: List[str]


class LocalFilters(BaseModel):
    issues: List[Tuple[str, Optional[int]]]
    origins: list[str]
    has_unknown_issue: bool


class DetailsFilters(BaseModel):
    all: GlobalFilters
    builds: LocalFilters
    boots: LocalFilters
    tests: LocalFilters


class CommonDetailsTestsResponse(BaseModel):
    tests: List[TestHistoryItem]


class CommonDetailsBootsResponse(BaseModel):
    boots: List[TestHistoryItem]
