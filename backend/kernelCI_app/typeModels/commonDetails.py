import json
from collections import defaultdict
from datetime import datetime
from typing import Optional, Union
from typing_extensions import Annotated

from pydantic import BaseModel, field_validator, Field
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.typeModels.common import StatusCount, make_default_validator
from kernelCI_app.typeModels.issues import Issue
from kernelCI_app.typeModels.databases import (
    NULL_STATUS,
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


class TestArchSummaryItem(BaseModel):
    # Disables automatic pytest test discovery for this class
    __test__ = False

    arch: str
    compiler: str
    status: StatusCount


class BuildArchitectures(StatusCount):
    compilers: Optional[list[str]] = []


class TestHistoryItem(BaseModel):
    id: str
    origin: Origin
    status: Optional[str]
    duration: Optional[Union[int, float]]
    path: Optional[str]
    start_time: Optional[Union[datetime, str]]
    environment_compatible: Optional[Union[str, list[str]]]
    config: Optional[str]
    log_url: Optional[str]
    architecture: Optional[str]
    compiler: Optional[str]
    environment_misc: Optional[EnvironmentMisc]
    lab: Optional[str]


class BuildHistoryItem(BaseModel):
    id: Build__Id
    origin: Origin
    architecture: Build__Architecture
    config_name: Build__ConfigName
    misc: Build__Misc
    config_url: Build__ConfigUrl
    compiler: Build__Compiler
    status: Annotated[
        Build__Status,
        make_default_validator(NULL_STATUS),
    ]
    duration: Build__Duration
    log_url: Build__LogUrl
    start_time: Build__StartTime
    git_repository_url: Checkout__GitRepositoryUrl
    git_repository_branch: Checkout__GitRepositoryBranch

    @field_validator("misc", mode="before")
    @classmethod
    def to_dict(cls, value) -> Optional[dict]:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError as err:
                log_message(
                    f"Invalid misc for BuildHistoryItem;\nType: {type(value)}\nError: {err.msg}"
                )
                return None
        elif isinstance(value, dict):
            return value
        elif value is None:
            return None
        else:
            log_message(f"Invalid misc for BuildHistoryItem;\nType: {type(value)}")


class TestSummary(BaseModel):
    # Disables automatic pytest test discovery for this class
    __test__ = False

    status: StatusCount
    origins: dict[str, StatusCount]
    architectures: list[TestArchSummaryItem]
    configs: dict[str, StatusCount]
    issues: list[Issue]
    unknown_issues: int
    fail_reasons: defaultdict[str, int]
    failed_platforms: set
    environment_compatible: Optional[dict] = None
    environment_misc: Optional[dict] = None
    platforms: Optional[dict[str, StatusCount]] = None
    labs: dict[str, StatusCount]


class BaseBuildSummary(BaseModel):
    status: StatusCount = Field(default_factory=StatusCount)
    origins: dict[str, StatusCount] = Field(default_factory=dict)
    architectures: dict[str, BuildArchitectures] = Field(default_factory=dict)
    configs: dict[str, StatusCount] = Field(default_factory=dict)
    labs: dict[str, StatusCount] = Field(default_factory=dict)


class BuildSummary(BaseBuildSummary):
    issues: list[Issue]
    unknown_issues: int


class Summary(BaseModel):
    builds: BuildSummary
    boots: TestSummary
    tests: TestSummary


class GlobalFilters(BaseModel):
    configs: list[str]
    architectures: list[str]
    compilers: list[str]


class LocalFilters(BaseModel):
    issues: list[tuple[str, Optional[int]]]
    origins: list[str]
    has_unknown_issue: bool
    labs: list[str]


class DetailsFilters(BaseModel):
    all: GlobalFilters
    builds: LocalFilters
    boots: LocalFilters
    tests: LocalFilters


class CommonDetailsTestsResponse(BaseModel):
    tests: list[TestHistoryItem]


class CommonDetailsBootsResponse(BaseModel):
    boots: list[TestHistoryItem]
