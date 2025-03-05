from datetime import datetime
from typing import List
from pydantic import BaseModel, RootModel

from kernelCI_app.typeModels.commonDetails import StatusCount
from kernelCI_app.typeModels.treeListing import TestStatusCount
from kernelCI_app.typeModels.databases import (
    Checkout__GitCommitHash,
    Checkout__GitCommitName,
    Checkout__GitCommitTags,
)


class TreeCommitsQueryParameters(BaseModel):
    origin: str
    git_url: str
    git_branch: str
    start_time_stamp_in_seconds: str
    end_time_stamp_in_seconds: str
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
