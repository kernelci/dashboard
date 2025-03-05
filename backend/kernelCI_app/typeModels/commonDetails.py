import json
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Union, Tuple, Any

from pydantic import BaseModel, field_validator
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.typeModels.issues import Issue
from kernelCI_app.typeModels.databases import (
    EnvironmentMisc,
    Build__Id,
    Build__Architecture,
    Build__ConfigName,
    Build__Misc,
    Build__ConfigUrl,
    Build__Compiler,
    Build__Valid,
    Build__LogUrl,
    Build__StartTime,
    Build__Duration,
    Checkout__GitRepositoryUrl,
    Checkout__GitRepositoryBranch,
)


class TestStatusCount(BaseModel):
    PASS: Optional[int] = 0
    ERROR: Optional[int] = 0
    FAIL: Optional[int] = 0
    SKIP: Optional[int] = 0
    MISS: Optional[int] = 0
    NULL: Optional[int] = 0


class BuildStatusCount(BaseModel):
    valid: Optional[int] = 0
    invalid: Optional[int] = 0
    null: Optional[int] = 0


class TestArchSummaryItem(BaseModel):
    arch: str
    compiler: str
    status: TestStatusCount


class BuildArchitectures(BuildStatusCount):
    compilers: Optional[List[str]] = []


class TestHistoryItem(BaseModel):
    id: str
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
    architecture: Build__Architecture
    config_name: Build__ConfigName
    misc: Build__Misc
    config_url: Build__ConfigUrl
    compiler: Build__Compiler
    valid: Build__Valid
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
        else:
            log_message("Invalid misc for BuildHistoryItem")


class TestSummary(BaseModel):
    status: TestStatusCount
    architectures: List[TestArchSummaryItem]
    configs: Dict[str, TestStatusCount]
    issues: List[Issue]
    unknown_issues: int
    fail_reasons: defaultdict[str, int]
    failed_platforms: Set
    environment_compatible: Optional[Dict] = None
    environment_misc: Optional[Dict] = None
    platforms: Optional[Dict[str, TestStatusCount]] = None


class BuildSummary(BaseModel):
    status: BuildStatusCount
    architectures: Dict[str, BuildArchitectures]
    configs: Dict[str, BuildStatusCount]
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
