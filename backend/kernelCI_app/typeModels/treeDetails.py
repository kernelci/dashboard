from typing import List, Optional

from kernelCI_app.typeModels.commonDetails import (
    BuildHistoryItem,
    DetailsFilters,
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


class SummaryResponse(BaseModel):
    common: TreeCommon
    summary: Summary
    filters: DetailsFilters


class TreeDetailsBuildsResponse(BaseModel):
    builds: List[BuildHistoryItem]


class TreeQueryParameters(BaseModel):
    origin: str
    git_url: str
    git_branch: str
