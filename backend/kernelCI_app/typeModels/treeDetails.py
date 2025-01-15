from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional, Union


class TreeLatestPathParameters(BaseModel):
    tree_name: str
    branch: str


class StatusCount(BaseModel):
    PASS: Optional[int] = None
    ERROR: Optional[int] = None
    FAIL: Optional[int] = None
    SKIP: Optional[int] = None
    NULL: Optional[int] = None


class TestArchSummaryItem(BaseModel):
    arch: str
    compiler: str
    status: StatusCount


class BuildsSummary(BaseModel):
    valid: int
    invalid: int
    null: int


class Configs(BaseModel):
    valid: int
    invalid: int
    null: int


class Architectures(BaseModel):
    valid: int
    invalid: int
    null: int
    compilers: List[str]


class BuildsSummaryDetails(BaseModel):
    builds: BuildsSummary
    configs: Dict[str, Configs]
    architectures: Dict[str, Architectures]


class IncidentsInfo(BaseModel):
    incidentsCount: int


class TestIssuesItem(BaseModel):
    id: str
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentsInfo


class TestEnvironmentCompatibleCount(BaseModel):
    FAIL: int
    PASS: int
    SKIP: int


class TestEnvironmentMiscCount(BaseModel):
    PASS: Optional[int] = None
    FAIL: Optional[int] = None
    ERROR: Optional[int] = None
    NULL: Optional[int] = None
    SKIP: Optional[int] = None


class BuildsIssuesItem(BaseModel):
    id: str
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentsInfo


class SummaryResponse(BaseModel):
    bootArchSummary: List
    testArchSummary: List[TestArchSummaryItem]
    buildsSummary: BuildsSummaryDetails
    bootFailReasons: Dict
    testFailReasons: Dict[str, int]
    testPlatformsWithErrors: List[str]
    bootPlatformsFailing: List
    testConfigs: Dict[str, StatusCount]
    bootConfigs: Dict
    testStatusSummary: StatusCount
    bootStatusSummary: Dict
    bootIssues: List
    testIssues: List[TestIssuesItem]
    testEnvironmentCompatible: Dict[str, TestEnvironmentCompatibleCount]
    bootEnvironmentCompatible: Dict
    testEnvironmentMisc: Dict[str, TestEnvironmentMiscCount]
    bootEnvironmentMisc: Dict
    hardwareUsed: List[str]
    failedTestsWithUnknownIssues: int
    failedBootsWithUnknownIssues: int
    buildsIssues: List[BuildsIssuesItem]
    failedBuildsWithUnknownIssues: int
    treeUrl: Optional[str]
    git_commit_tags: Optional[List]


class TestHistory(BaseModel):
    id: str
    status: Optional[str]
    duration: Optional[Union[int, float]]
    path: Optional[str]
    startTime: Optional[Union[datetime, str]]
    hardware: Optional[Union[str, List[str]]]


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
