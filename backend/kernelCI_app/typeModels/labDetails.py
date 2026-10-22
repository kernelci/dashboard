from datetime import date, datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field

from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.commonListing import ListingQueryParameters
from kernelCI_app.typeModels.issues import Issue


class LabDetailsQueryParameters(ListingQueryParameters):
    """Origin and interval match the labs listing."""

    tree: Annotated[
        list[str],
        Field(
            default_factory=list,
            description=(
                "Optional tree/branch filter as `tree_name/git_branch` "
                "(repeat for multiple trees)."
            ),
        ),
    ]


class LabDailyPoint(BaseModel):
    day: date
    pass_count: int = 0
    fail_count: int = 0
    inconclusive_count: int = 0


class LabTreeDailySeries(BaseModel):
    builds: list[LabDailyPoint]
    boots: list[LabDailyPoint]
    tests: list[LabDailyPoint]


class LabDetailsTreeItem(BaseModel):
    key: str
    tree_name: str
    git_branch: str
    commit_name: Optional[str] = None
    commit_hash: Optional[str] = None
    builds: StatusCount
    boots: StatusCount
    tests: StatusCount
    build_issues: list[Issue]
    boot_issues: list[Issue]
    test_issues: list[Issue]
    daily: LabTreeDailySeries


class LabFrequencyCounts(BaseModel):
    name: str
    count: int


class LabDistribution(BaseModel):
    platforms: list[LabFrequencyCounts]
    configs: list[LabFrequencyCounts]
    compilers: list[LabFrequencyCounts]
    architectures: list[LabFrequencyCounts]
    build_status: StatusCount
    boot_status: StatusCount
    test_status: StatusCount


class LabFillStats(BaseModel):
    checkout_total: int
    checkouts_built: int
    checkouts_booted: int
    checkouts_tested: int
    builds_total: int
    builds_with_duration: int
    runs_total: int
    runs_with_duration: int
    runs_with_platform: int
    runs_with_log_url: int
    runs_with_log_excerpt: int


class LabDetailsResponse(BaseModel):
    lab_name: str
    trees: list[LabDetailsTreeItem]
    distribution: LabDistribution
    fill: LabFillStats


class LabBuildRowItem(BaseModel):
    tree_name: str
    git_branch: str
    config_name: str
    architecture: str
    compiler: str
    status: str
    start_time: Optional[datetime] = None
    duration: Optional[float] = None


class LabBootRowItem(BaseModel):
    tree_name: str
    git_branch: str
    platform: str
    config_name: str
    architecture: str
    compiler: str
    status: str
    start_time: Optional[datetime] = None
    duration: Optional[float] = None
    log_url: Optional[str] = None
    log_excerpt: Optional[str] = None


class LabTestRowItem(BaseModel):
    id: str
    status: str
    path: Optional[str] = None
    start_time: Optional[datetime] = None
    duration: Optional[float] = None
    tree_name: str
    git_repository_branch: str
    lab: str
    config_name: Optional[str] = None
    architecture: Optional[str] = None
    compiler: Optional[str] = None
    platform: Optional[str] = None
    log_url: Optional[str] = None
    log_excerpt: Optional[str] = None
    environment_misc: Optional[dict] = None


class LabBuildRowsResponse(BaseModel):
    builds: list[LabBuildRowItem]


class LabBootRowsResponse(BaseModel):
    boots: list[LabBootRowItem]


class LabTestRowsResponse(BaseModel):
    tests: list[LabTestRowItem]


class LabAttentionItem(BaseModel):
    kind: Literal["boot", "test"]
    path: Optional[str] = None
    platform: str
    tree_name: str
    git_branch: str
    commit_name: Optional[str] = None
    commit_hash: Optional[str] = None
    config_name: str
    architecture: str
    compiler: str
    last_failure_date: date
    passed_labs: list[str]


class LabAttentionResponse(BaseModel):
    items: list[LabAttentionItem]
