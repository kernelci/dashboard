from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class TestStatusCount(BaseModel):
    PASS: Optional[int] = None
    ERROR: Optional[int] = None
    FAIL: Optional[int] = None
    SKIP: Optional[int] = None
    NULL: Optional[int] = None


class BuildStatusCount(BaseModel):
    valid: int
    invalid: int
    null: int


class TestArchSummaryItem(BaseModel):
    arch: str
    compiler: str
    status: TestStatusCount


class BuildConfigs(BuildStatusCount):
    valid: int
    invalid: int
    null: int


class IncidentsInfo(BaseModel):
    incidentsCount: int


class TestIssuesItem(BaseModel):
    id: str
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentsInfo


class BuildsIssuesItem(BaseModel):
    id: str
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentsInfo


class BuildArchitectures(BuildStatusCount):
    compilers: List[str]


class Misc(BaseModel):
    platform: str


class TestHistoryItem(BaseModel):
    id: str
    status: Optional[str]
    duration: Optional[Union[int, float]]
    path: Optional[str]
    start_time: Optional[Union[datetime, str]]
    environment_compatible: Optional[Union[str, List[str]]] = None
    # TODO: When these fields are added to hardwareDetails, there shouldn't be any need for `= None` anymore
    config: Optional[str] = None
    log_url: Optional[str] = None
    architecture: Optional[str] = None
    compiler: Optional[str] = None
    misc: Optional[Misc] = None


class BuildHistoryItem(BaseModel):
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


class TestSummary(BaseModel):
    status: TestStatusCount
    architectures: List[TestArchSummaryItem]
    configs: Dict[str, TestStatusCount]
    issues: List[TestIssuesItem]
    unknown_issues: int
    fail_reasons: Dict[str, int]
    failed_platforms: List[str]
    environment_compatible: Optional[Dict] = None
    environment_misc: Optional[Dict] = None
    platforms: Optional[Dict[str, TestStatusCount]] = None


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
