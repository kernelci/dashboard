from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from kernelCI_app.typeModels.commonDetails import (
    BuildHistoryItem,
    GlobalFilters,
    LocalFilters,
    Summary,
    TestHistoryItem,
)
from kernelCI_app.typeModels.databases import (
    StatusValues,
    Checkout__TreeName,
    Checkout__GitRepositoryBranch,
)
from pydantic import BaseModel, BeforeValidator, Field


def process_status(value: Any) -> Any:
    if value is None:
        return "NULL"
    return value


class DefaultRecordValues(BaseModel):
    status: Annotated[StatusValues, BeforeValidator(process_status)]


class HardwareDetailsPostBody(BaseModel):
    origin: str = Field(default="maestro")
    startTimestampInSeconds: Union[str, int]
    endTimestampInSeconds: Union[str, int]
    selectedCommits: Dict[str, str]
    filter: Optional[Dict]


class CommitHead(BaseModel):
    treeName: str
    repositoryUrl: str
    branch: str
    commitHash: str


class CommitHistoryPostBody(BaseModel):
    origin: str = Field(default="maestro")
    startTimestampInSeconds: Union[str, int]
    endTimestampInSeconds: Union[str, int]
    commitHeads: List[CommitHead]


class CommitHistoryValidCheckout(BaseModel):
    git_commit_hash: str
    tree_name: str
    git_repository_branch: str
    git_repository_url: str
    git_commit_tags: Optional[List[str]] = []
    git_commit_name: Optional[str]
    start_time: datetime


class Tree(BaseModel):
    index: str
    tree_name: Optional[str]
    git_repository_branch: Optional[str]
    git_repository_url: Optional[str]
    head_git_commit_name: Optional[str]
    head_git_commit_hash: Optional[str]
    head_git_commit_tag: Optional[List[str]]
    selected_commit_status: Optional[Dict]
    is_selected: Optional[bool]


class HardwareCommon(BaseModel):
    trees: List[Tree]
    compatibles: List[str]


class HardwareTestLocalFilters(LocalFilters):
    platforms: List[str]


class HardwareDetailsFilters(BaseModel):
    all: GlobalFilters
    builds: LocalFilters
    boots: HardwareTestLocalFilters
    tests: HardwareTestLocalFilters


class HardwareTestHistoryItem(TestHistoryItem):
    tree_name: Checkout__TreeName
    git_repository_branch: Checkout__GitRepositoryBranch


class HardwareBuildHistoryItem(BuildHistoryItem):
    tree_name: Optional[str]
    issue_id: Optional[str]
    issue_version: Optional[str]


class HardwareDetailsFullResponse(BaseModel):
    builds: List[HardwareBuildHistoryItem]
    boots: List[HardwareTestHistoryItem]
    tests: List[HardwareTestHistoryItem]
    summary: Summary
    filters: HardwareDetailsFilters
    common: HardwareCommon


class HardwareDetailsSummaryResponse(BaseModel):
    summary: Summary
    filters: HardwareDetailsFilters
    common: HardwareCommon


class HardwareDetailsBuildsResponse(BaseModel):
    builds: List[HardwareBuildHistoryItem]


class HardwareDetailsBootsResponse(BaseModel):
    boots: List[HardwareTestHistoryItem]


class HardwareDetailsTestsResponse(BaseModel):
    tests: List[HardwareTestHistoryItem]


PossibleTestType = Literal["test", "boot"]
