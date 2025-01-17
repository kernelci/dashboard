from datetime import datetime
from typing import Dict, List, Optional, Union

from kernelCI_app.typeModels.issues import Issue
from pydantic import BaseModel


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


class Misc(BaseModel):
    platform: str


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
    misc: Optional[Misc]


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
    issues: List[Issue]
    unknown_issues: int
    fail_reasons: Dict[str, int]
    failed_platforms: List[str]
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
