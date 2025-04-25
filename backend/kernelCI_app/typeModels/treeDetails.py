from typing import List, Optional

from kernelCI_app.typeModels.commonDetails import (
    BuildHistoryItem,
    DetailsFilters,
    Summary,
    CommonDetailsBootsResponse,
    CommonDetailsTestsResponse,
)
from kernelCI_app.typeModels.treeListing import BaseCheckouts
from pydantic import BaseModel
from kernelCI_app.constants.general import DEFAULT_ORIGIN


class TreeLatestPathParameters(BaseModel):
    tree_name: str
    branch: str


class TreeLatestQueryParameters(BaseModel):
    origin: str = DEFAULT_ORIGIN


class TreeLatestResponse(BaseCheckouts):
    api_url: str
    tree_name: str


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


class TreeDetailsFullResponse(
    TreeDetailsBuildsResponse,
    CommonDetailsBootsResponse,
    CommonDetailsTestsResponse,
    SummaryResponse,
):
    pass
