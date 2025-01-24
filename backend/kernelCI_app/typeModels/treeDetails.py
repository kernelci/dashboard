from typing import List, Optional

from kernelCI_app.typeModels.commonDetails import (
    BuildHistoryItem,
    Summary,
)
from pydantic import BaseModel


class TreeLatestPathParameters(BaseModel):
    tree_name: str
    branch: str


class TreeCommon(BaseModel):
    hardware: Optional[List[str]]
    tree_url: Optional[str]
    git_commit_tags: Optional[List[str]]


class TreeGlobalFilters(BaseModel):
    configs: List[str]
    architectures: List[str]
    compilers: List[str]


class TreeLocalFilters(BaseModel):
    issues: List[str]


class TreeFilters(BaseModel):
    all: TreeGlobalFilters
    builds: TreeLocalFilters
    boots: TreeLocalFilters
    tests: TreeLocalFilters


class SummaryResponse(BaseModel):
    common: TreeCommon
    summary: Summary
    filters: TreeFilters


class TreeDetailsBuildsResponse(BaseModel):
    builds: List[BuildHistoryItem]


class TreeQueryParameters(BaseModel):
    origin: str = "maestro"
    git_url: str
    git_branch: str
