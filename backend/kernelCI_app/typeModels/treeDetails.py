from typing import List, Optional

from kernelCI_app.typeModels.commonDetails import (
    BuildHistoryItem,
    DetailsFilters,
    Summary,
    CommonDetailsBootsResponse,
    CommonDetailsTestsResponse,
)
from kernelCI_app.typeModels.treeListing import BaseCheckouts
from pydantic import BaseModel, Field
from kernelCI_app.constants.general import DEFAULT_ORIGIN


class TreeLatestPathParameters(BaseModel):
    tree_name: str = Field(description="Name of the tree")
    git_branch: str = Field(description="Git branch name of the tree")
    commit_hash: Optional[str] = Field(description="Commit of the tree")


class TreeLatestQueryParameters(BaseModel):
    origin: str = Field(DEFAULT_ORIGIN, description="Origin filter for the tree")


class TreeLatestResponse(BaseCheckouts):
    api_url: str
    old_api_url: str
    tree_name: str
    git_repository_branch: str


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
    origin: str = Field(description="Origin of the tree")
    git_url: str = Field(description="Git repository URL of the tree")
    git_branch: str = Field(description="Git branch name of the tree")


class TreeDetailsFullResponse(
    TreeDetailsBuildsResponse,
    CommonDetailsBootsResponse,
    CommonDetailsTestsResponse,
    SummaryResponse,
):
    pass
