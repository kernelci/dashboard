from typing import Literal, Optional
from pydantic import BaseModel, Field

from kernelCI_app.typeModels.databases import (
    Origin,
    Test__Id,
    Build__Id,
    Test__Status,
    Test__Path,
    Test__LogExcerpt,
    Test__LogUrl,
    Test__Misc,
    Test__EnvironmentMisc,
    Test__StartTime,
    Test__EnvironmentCompatible,
    Test__OutputFiles,
    Build__Compiler,
    Build__Architecture,
    Build__ConfigName,
    Checkout__GitCommitHash,
    Checkout__GitRepositoryBranch,
    Checkout__GitRepositoryUrl,
    Checkout__GitCommitTags,
    Checkout__TreeName,
    Timestamp,
)


class TestDetailsResponse(BaseModel):
    id: Test__Id
    build_id: Build__Id
    status: Test__Status
    path: Test__Path
    log_excerpt: Test__LogExcerpt
    log_url: Test__LogUrl
    misc: Test__Misc
    environment_misc: Test__EnvironmentMisc
    start_time: Test__StartTime
    environment_compatible: Test__EnvironmentCompatible
    output_files: Test__OutputFiles
    compiler: Build__Compiler = Field(validation_alias="build__compiler")
    architecture: Build__Architecture = Field(validation_alias="build__architecture")
    config_name: Build__ConfigName = Field(validation_alias="build__config_name")
    git_commit_hash: Checkout__GitCommitHash = Field(
        validation_alias="build__checkout__git_commit_hash"
    )
    git_repository_branch: Checkout__GitRepositoryBranch = Field(
        validation_alias="build__checkout__git_repository_branch"
    )
    git_repository_url: Checkout__GitRepositoryUrl = Field(
        validation_alias="build__checkout__git_repository_url"
    )
    git_commit_tags: Checkout__GitCommitTags = Field(
        validation_alias="build__checkout__git_commit_tags"
    )
    tree_name: Checkout__TreeName = Field(validation_alias="build__checkout__tree_name")
    origin: Origin = Field(validation_alias="build__checkout__origin")
    field_timestamp: Timestamp


type PossibleRegressionType = Literal["regression", "fixed", "unstable", "pass", "fail"]


class TestStatusHistoryItem(BaseModel):
    field_timestamp: Timestamp
    id: Test__Id
    status: Test__Status
    git_commit_hash: Checkout__GitCommitHash = Field(
        validation_alias="build__checkout__git_commit_hash"
    )


class TestStatusHistoryResponse(BaseModel):
    status_history: list[TestStatusHistoryItem]
    regression_type: PossibleRegressionType


class TestStatusHistoryRequest(BaseModel):
    path: Test__Path = None
    origin: Origin
    git_repository_url: Checkout__GitRepositoryUrl = None
    git_repository_branch: Checkout__GitRepositoryBranch = None
    platform: Optional[str] = None
    current_test_timestamp: Timestamp
