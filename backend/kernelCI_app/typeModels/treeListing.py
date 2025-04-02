from typing import List
from kernelCI_app.typeModels.commonDetails import StatusCount
from kernelCI_app.typeModels.databases import (
    Checkout__GitCommitHash,
    Checkout__GitCommitName,
    Checkout__GitCommitTags,
    Checkout__TreeName,
    Checkout__Id,
    Checkout__PatchsetHash,
    Checkout__GitRepositoryBranch,
    Checkout__GitRepositoryUrl,
    Checkout__OriginBuildsFinishTime,
    Checkout__OriginTestsFinishTime,
    Timestamp,
)
from pydantic import BaseModel, Field, RootModel


class TestStatusCount(BaseModel):
    pass_count: int = Field(alias="pass")
    error_count: int = Field(alias="error")
    fail_count: int = Field(alias="fail")
    skip_count: int = Field(alias="skip")
    miss_count: int = Field(alias="miss")
    done_count: int = Field(alias="done")
    null_count: int = Field(alias="null")


class BaseCheckouts(BaseModel):
    git_repository_url: Checkout__GitRepositoryUrl
    git_commit_hash: Checkout__GitCommitHash
    git_commit_name: Checkout__GitCommitName


class CommonCheckouts(BaseCheckouts):
    git_repository_branch: Checkout__GitRepositoryBranch
    start_time: Timestamp
    origin_builds_finish_time: Checkout__OriginBuildsFinishTime
    origin_tests_finish_time: Checkout__OriginTestsFinishTime


class Checkout(CommonCheckouts):
    build_status: StatusCount
    test_status: TestStatusCount
    boot_status: TestStatusCount
    tree_name: Checkout__TreeName
    git_commit_tags: List[Checkout__GitCommitTags]


class CheckoutFast(CommonCheckouts):
    id: Checkout__Id
    tree_name: Checkout__TreeName
    patchset_hash: Checkout__PatchsetHash
    git_commit_tags: Checkout__GitCommitTags


class TreeListingResponse(RootModel):
    root: List[Checkout]


class TreeListingFastResponse(RootModel):
    root: List[CheckoutFast]
