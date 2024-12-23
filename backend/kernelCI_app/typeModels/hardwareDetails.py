from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, Union

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
    start_time: datetime
