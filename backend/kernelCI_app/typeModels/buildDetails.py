from typing import List, Optional

from pydantic import BaseModel, RootModel
from typing_extensions import Annotated

from kernelCI_app.typeModels.common import make_default_validator
from kernelCI_app.typeModels.commonDetails import BuildHistoryItem
from kernelCI_app.typeModels.databases import (
    NULL_STATUS,
    Build__Command,
    Build__Comment,
    Build__InputFiles,
    Build__LogExcerpt,
    Build__OutputFiles,
    Checkout__GitCommitHash,
    Checkout__GitCommitName,
    Checkout__GitCommitTags,
    Checkout__Id,
    Checkout__TreeName,
    Origin,
    StatusValues,
    Test__Duration,
    Test__EnvironmentCompatible,
    Test__EnvironmentMisc,
    Test__Id,
    Test__Path,
    Test__StartTime,
    Timestamp,
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
    origin: Optional[Origin]
    log_excerpt: Build__LogExcerpt
    input_files: Build__InputFiles
    output_files: Build__OutputFiles
    build_origin: Origin


class BuildTestItem(BaseModel):
    id: Test__Id
    status: Annotated[StatusValues, make_default_validator(NULL_STATUS)]
    duration: Test__Duration
    path: Test__Path
    start_time: Test__StartTime
    environment_compatible: Test__EnvironmentCompatible
    environment_misc: Test__EnvironmentMisc
    lab: Optional[str]


class BuildTestsResponse(RootModel):
    root: List[BuildTestItem]
