from typing import Dict, List, Optional

from kernelCI_app.typeModels.commonDetails import (
    Summary,
    BuildHistoryItem,
    TestArchSummaryItem,
    TestIssuesItem,
    TestStatusCount,
    TestHistoryItem,
)
from pydantic import BaseModel


class TreeLatestPathParameters(BaseModel):
    tree_name: str
    branch: str


class TestSummary(BaseModel):
    status: TestStatusCount
    architectures: List[TestArchSummaryItem]
    configs: Dict[str, TestStatusCount]
    issues: List[TestIssuesItem]
    unknown_issues: int
    environment_compatible: Dict[str, TestStatusCount]
    environment_misc: Dict[str, TestStatusCount]
    fail_reasons: Dict[str, int]
    failed_platforms: List[str]


class TreeSummary(Summary):
    hardware: Optional[List[str]]
    tree_url: Optional[str]
    git_commit_tags: Optional[List[str]]


class SummaryResponse(BaseModel):
    summary: TreeSummary


class BootResponse(BaseModel):
    bootHistory: List[TestHistoryItem]


class TestResponse(BaseModel):
    testHistory: List[TestHistoryItem]


class BuildsResponse(BaseModel):
    builds: List[BuildHistoryItem]


class TreeQueryParameters(BaseModel):
    origin: str = "maestro"
    git_url: str
    git_branch: str
