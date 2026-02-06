from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, RootModel

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.treeListing import TestStatusCount
from pydantic import Field
from kernelCI_app.typeModels.databases import (
    Checkout__GitCommitHash,
    Checkout__GitCommitName,
    Checkout__GitCommitTags,
)


class DirectTreeCommitsQueryParameters(BaseModel):
    origin: str = Field(
        DEFAULT_ORIGIN, description=DocStrings.TREE_COMMIT_ORIGIN_DESCRIPTION
    )
    start_time_stamp_in_seconds: Optional[str] = Field(
        None, description=DocStrings.TREE_COMMIT_START_TS_DESCRIPTION
    )
    end_time_stamp_in_seconds: Optional[str] = Field(
        None, description=DocStrings.TREE_COMMIT_END_TS_DESCRIPTION
    )
    # TODO: Add filters field in this model


class TreeCommitsQueryParameters(DirectTreeCommitsQueryParameters):
    git_branch: Optional[str] = Field(
        description=DocStrings.TREE_COMMIT_GIT_BRANCH_DESCRIPTION
    )
    git_url: Optional[str] = Field(
        description=DocStrings.TREE_COMMIT_GIT_URL_DESCRIPTION
    )


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
