from pydantic import BaseModel, Field
from typing import Dict, Optional, Union

class PostBody(BaseModel):
    origin: str = Field(default="maestro")
    startTimestampInSeconds: Union[str, int]
    endTimestampInSeconds: Union[str, int]
    selectedCommits: Dict[str, str]
    filter: Optional[Dict]


class CommitHistoryPostBody(BaseModel):
    origin: str = Field(default="maestro")
    startTimestampInSeconds: Union[str, int]
    endTimestampInSeconds: Union[str, int]
    # Keys will be tree name + commit branch.
    commitHeads: Dict[str, str]

class CommitHistoryQuerysetItem(BaseModel):
    git_commit_hash: str
    tree_name: str
    git_repository_branch: str
    git_repository_url: str
