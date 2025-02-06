from datetime import datetime
from typing import List
from pydantic import BaseModel, RootModel, Field

from kernelCI_app.typeModels.commonDetails import BuildStatusCount
from kernelCI_app.typeModels.databases import (
    Checkout__GitCommitHash,
    Checkout__GitCommitName
)


class TreeCommitsTestStatusCount(BaseModel):
    fail_count: int = Field(alias="fail")
    error_count: int = Field(alias="error")
    miss_count: int = Field(alias="miss")
    pass_count: int = Field(alias="pass")
    done_count: int = Field(alias="done")
    skip_count: int = Field(alias="skip")
    null_count: int = Field(alias="null")


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
    earliest_start_time: datetime
    builds: BuildStatusCount
    boots: TreeCommitsTestStatusCount
    tests: TreeCommitsTestStatusCount


class TreeCommitsResponse(RootModel):
    root: List[TreeCommitsData]
