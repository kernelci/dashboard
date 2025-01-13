from pydantic import BaseModel
from typing import List, Dict, Optional


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
