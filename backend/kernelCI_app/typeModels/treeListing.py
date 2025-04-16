from typing import List
from kernelCI_app.typeModels.common import StatusCount
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

    def __add__(self, other: "TestStatusCount") -> "TestStatusCount":
        return TestStatusCount(
            **{
                "pass": self.pass_count + other.pass_count,
                "error": self.error_count + other.error_count,
                "fail": self.fail_count + other.fail_count,
                "skip": self.skip_count + other.skip_count,
                "miss": self.miss_count + other.miss_count,
                "done": self.done_count + other.done_count,
                "null": self.null_count + other.null_count,
            }
        )


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
    id: Checkout__Id = Field(validation_alias="checkout_id")
    build_status: StatusCount
    test_status: TestStatusCount
    boot_status: TestStatusCount
    tree_name: Checkout__TreeName
    git_commit_tags: list[Checkout__GitCommitTags]

    def add_counts(
        self,
        build_status: StatusCount,
        test_status: TestStatusCount,
        boot_status: TestStatusCount,
    ) -> None:
        self.build_status += build_status
        self.test_status += test_status
        self.boot_status += boot_status

    def combine_tags(self, tags: list[Checkout__GitCommitTags]) -> None:
        if not tags:
            return

        existing_tags = set(self.git_commit_tags)

        for tag in tags:
            if tag not in existing_tags:
                existing_tags.add(tag)
                self.git_commit_tags.append(tag)


class CheckoutFast(CommonCheckouts):
    id: Checkout__Id
    tree_name: Checkout__TreeName
    patchset_hash: Checkout__PatchsetHash
    git_commit_tags: Checkout__GitCommitTags


class TreeListingResponse(RootModel):
    root: List[Checkout]


class TreeListingFastResponse(RootModel):
    root: List[CheckoutFast]
