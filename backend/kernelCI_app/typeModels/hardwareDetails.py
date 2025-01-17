from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from kernelCI_app.typeModels.commonDetails import BuildHistoryItem, Summary, TestHistoryItem
from kernelCI_app.typeModels.databases import StatusValues
from pydantic import BaseModel, BeforeValidator, Field


def process_status(value: Any) -> Any:
    if value is None:
        return "NULL"
    return value


class DefaultRecordValues(BaseModel):
    status: Annotated[StatusValues, BeforeValidator(process_status)]


class PostBody(BaseModel):
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


class HardwareSummary(Summary):
    trees: List[Tree]
    configs: List[str]
    architectures: List[str]
    compilers: List[str]
    compatibles: List[str]


class BuildResponse(BaseModel):
    builds: List[BuildHistoryItem]


class HardwareDetailsFullResponse(BaseModel):
    builds: List[BuildHistoryItem]
    boots: List[TestHistoryItem]
    tests: List[TestHistoryItem]
    summary: HardwareSummary


type HardwareTreeList = List[Dict[str, str]]

PossibleTestType = Literal["test", "boot"]
