from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional, Set, Union


class TreeLatestPathParameters(BaseModel):
    tree_name: str
    branch: str


class TestStatusCount(BaseModel):
    PASS: Optional[int] = None
    ERROR: Optional[int] = None
    FAIL: Optional[int] = None
    SKIP: Optional[int] = None
    NULL: Optional[int] = None


class TestArchSummaryItem(BaseModel):
    arch: str
    compiler: str
    status: TestStatusCount


class BuildStatusCount(BaseModel):
    valid: int
    invalid: int
    null: int


class BuildConfigs(BuildStatusCount):
    valid: int
    invalid: int
    null: int


class BuildArchitectures(BuildStatusCount):
    compilers: List[str]


class IncidentsInfo(BaseModel):
    incidentsCount: int


class TestIssuesItem(BaseModel):
    id: str
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentsInfo


class TestEnvironmentCompatibleCount(TestStatusCount):
    pass


class TestEnvironmentMiscCount(TestStatusCount):
    pass


class BuildsIssuesItem(BaseModel):
    id: str
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentsInfo


class TestSummary(BaseModel):
    status: TestStatusCount
    architectures: List[TestArchSummaryItem]
    configs: Dict[str, TestStatusCount]
    issues: List[TestIssuesItem]
    unknown_issues: int
    enviroment_compatible: Dict[str, TestEnvironmentCompatibleCount]
    enviroment_misc: Dict[str, TestEnvironmentMiscCount]
    fail_reasons: Dict[str, int]
    failed_platforms: List[str]


class BuildSummary(BaseModel):
    status: BuildStatusCount
    architectures: Dict[str, BuildArchitectures]
    configs: Dict[str, BuildConfigs]
    issues: List[BuildsIssuesItem]
    unknown_issues: int


class Summary(BaseModel):
    builds: BuildSummary
    boots: TestSummary
    tests: TestSummary
    hardware: Set[str]
    tree_url: str
    git_commit_tags: Optional[List[str]]


class SummaryResponse(BaseModel):
    summary: Summary


class Misc(BaseModel):
    platform: str


class TestHistory(BaseModel):
    id: str
    status: Optional[str]
    duration: Optional[Union[int, float]]
    path: Optional[str]
    startTime: Optional[Union[datetime, str]]
    hardware: Optional[Union[str, List[str]]]
    config: Optional[str]
    log_url: Optional[str]
    architecture: Optional[str]
    compiler: Optional[str]
    misc: Optional[Misc]


class BootResponse(BaseModel):
    bootHistory: List[TestHistory]


class TestResponse(BaseModel):
    testHistory: List[TestHistory]


class BuildItem(BaseModel):
    id: str
    architecture: Optional[str]
    config_name: Optional[str]
    misc: Optional[dict]
    config_url: Optional[str]
    compiler: Optional[str]
    valid: Optional[bool]
    duration: Optional[Union[int, float]]
    log_url: Optional[str]
    start_time: Optional[Union[datetime, str]]
    git_repository_url: Optional[str]
    git_repository_branch: Optional[str]


class BuildsResponse(BaseModel):
    builds: List[BuildItem]


class TreeQueryParameters(BaseModel):
    origin: str = "maestro"
    git_url: str
    git_branch: str
