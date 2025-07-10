from typing import List
from typing_extensions import Annotated
from pydantic import BaseModel, RootModel

from kernelCI_app.typeModels.common import make_default_validator
from kernelCI_app.typeModels.commonDetails import BuildHistoryItem
from kernelCI_app.typeModels.databases import (
    NULL_STATUS,
    Origin,
    StatusValues,
    Timestamp,
    Checkout__Id,
    Checkout__TreeName,
    Checkout__GitCommitHash,
    Checkout__GitCommitName,
    Checkout__GitCommitTags,
    Build__Command,
    Build__Comment,
    Build__LogExcerpt,
    Build__InputFiles,
    Build__OutputFiles,
    Test__Id,
    Test__Duration,
    Test__Path,
    Test__StartTime,
    Test__EnvironmentCompatible,
    Test__EnvironmentMisc,
)


class BuildDetailsResponse(BuildHistoryItem):
    _timestamp: Timestamp
    checkout_id: Checkout__Id
    command: Build__Command
    comment: Build__Comment
    tree_name: Checkout__TreeName
    git_commit_hash: Checkout__GitCommitHash
    git_commit_name: Checkout__GitCommitName
    git_commit_tags: Checkout__GitCommitTags
    origin: Origin
    log_excerpt: Build__LogExcerpt
    input_files: Build__InputFiles
    output_files: Build__OutputFiles


class BuildTestItem(BaseModel):
    id: Test__Id
    status: Annotated[StatusValues, make_default_validator(NULL_STATUS)]
    duration: Test__Duration
    path: Test__Path
    start_time: Test__StartTime
    environment_compatible: Test__EnvironmentCompatible
    environment_misc: Test__EnvironmentMisc


class BuildTestsResponse(RootModel):
    root: List[BuildTestItem]
