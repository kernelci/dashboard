from typing import List, Optional

from pydantic import BaseModel, Field, RootModel

from kernelCI_app.helpers.logger import log_message
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.commonListing import StatusCountV2
from kernelCI_app.typeModels.databases import (
    Checkout__GitCommitHash,
    Checkout__GitCommitName,
    Checkout__GitCommitTags,
    Checkout__GitRepositoryBranch,
    Checkout__GitRepositoryUrl,
    Checkout__Id,
    Checkout__OriginBuildsFinishTime,
    Checkout__OriginTestsFinishTime,
    Checkout__PatchsetHash,
    Checkout__TreeName,
    Origin,
    Timestamp,
)


class TestStatusCount(BaseModel):
    # Disables automatic pytest test discovery for this class
    __test__ = False

    pass_count: int = Field(alias="pass", default=0)
    error_count: int = Field(alias="error", default=0)
    fail_count: int = Field(alias="fail", default=0)
    skip_count: int = Field(alias="skip", default=0)
    miss_count: int = Field(alias="miss", default=0)
    done_count: int = Field(alias="done", default=0)
    null_count: int = Field(alias="null", default=0)

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

    def increment(self, status: Optional[str], count: int = 1) -> None:
        if status is None:
            status = "NULL"
        try:
            status_prop = f"{status.lower()}_count"
            setattr(self, status_prop, getattr(self, status_prop) + count)
        except AttributeError:
            log_message(f"Unknown status: {status}")


class BaseCheckouts(BaseModel):
    git_repository_url: Checkout__GitRepositoryUrl
    git_commit_hash: Checkout__GitCommitHash
    git_commit_name: Checkout__GitCommitName
    origin: Origin


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


class CheckoutFast(CommonCheckouts):
    id: Checkout__Id
    tree_name: Checkout__TreeName
    patchset_hash: Checkout__PatchsetHash
    git_commit_tags: Checkout__GitCommitTags


class TreeListingResponse(RootModel):
    root: List[Checkout]


class TreeListingFastResponse(RootModel):
    root: List[CheckoutFast]


class TreeListingItem(BaseModel):
    id: Checkout__Id = Field(validation_alias="checkout_id")
    build_status: StatusCountV2
    boot_status: StatusCountV2
    test_status: StatusCountV2
    tree_name: Checkout__TreeName
    git_commit_tags: Checkout__GitCommitTags
    origin: Origin
    git_repository_url: Checkout__GitRepositoryUrl
    git_repository_branch: Checkout__GitRepositoryBranch
    git_commit_hash: Checkout__GitCommitHash
    git_commit_name: Checkout__GitCommitName
    start_time: Timestamp


class TreeListingResponseV2(RootModel):
    root: list[TreeListingItem]
