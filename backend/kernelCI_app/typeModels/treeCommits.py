from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, RootModel

from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.treeListing import TestStatusCount
from pydantic import Field
from kernelCI_app.typeModels.databases import (
    Checkout__GitCommitHash,
    Checkout__GitCommitName,
    Checkout__GitCommitTags,
)


class TreeCommitsQueryParameters(BaseModel):
    origin: str = Field(description="The origin of the tree")
    git_url: Optional[str] = Field(None, description="Git repository URL of the tree")
    git_branch: Optional[str] = Field(None, description="Branch name of the tree")
    start_time_stamp_in_seconds: Optional[str] = Field(
        None, description="Start time filter for tree commits"
    )
    end_time_stamp_in_seconds: Optional[str] = Field(
        None, description="End time filter for tree commits"
    )
    # TODO: Add filters field in this model


class TreeCommitsData(BaseModel):
    git_commit_hash: Checkout__GitCommitHash
    git_commit_name: Checkout__GitCommitName
    git_commit_tags: Checkout__GitCommitTags
    earliest_start_time: datetime
    builds: StatusCount
    boots: TestStatusCount
    tests: TestStatusCount


class TreeCommitsResponse(RootModel):
    root: List[TreeCommitsData]
