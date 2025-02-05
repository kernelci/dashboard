from pydantic import BaseModel, Field

from kernelCI_app.typeModels.databases import (
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
