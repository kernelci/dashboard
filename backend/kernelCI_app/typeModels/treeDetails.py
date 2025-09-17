from typing import List, Optional

from kernelCI_app.constants.localization import DocStrings
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
    tree_name: str = Field(description=DocStrings.TREE_LATEST_TREE_NAME_DESCRIPTION)
    git_branch: str = Field(description=DocStrings.TREE_LATEST_GIT_BRANCH_DESCRIPTION)


class TreeLatestQueryParameters(BaseModel):
    origin: str = Field(
        DEFAULT_ORIGIN, description=DocStrings.TREE_LATEST_ORIGIN_DESCRIPTION
    )
    commit_hash: Optional[str] = Field(
        None, description=DocStrings.TREE_LATEST_COMMIT_HASH_DESCRIPTION
    )


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


class DirectTreeQueryParameters(BaseModel):
    origin: str = Field(
        DEFAULT_ORIGIN, description=DocStrings.TREE_QUERY_ORIGIN_DESCRIPTION
    )


class DirectTreePathParameters(BaseModel):
    tree_name: str
    git_branch: str
    commit_hash: str


class TreeQueryParameters(DirectTreeQueryParameters):
    git_branch: str = Field(description=DocStrings.DEFAULT_GIT_BRANCH_DESCRIPTION)
    git_url: str = Field(description=DocStrings.TREE_QUERY_GIT_URL_DESCRIPTION)


class TreeDetailsFullResponse(
    TreeDetailsBuildsResponse,
    CommonDetailsBootsResponse,
    CommonDetailsTestsResponse,
    SummaryResponse,
):
    pass
