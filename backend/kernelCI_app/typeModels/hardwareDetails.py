from pydantic import BaseModel, Field
from typing import Dict, Optional, Union, List
from datetime import datetime


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
    start_time: datetime
