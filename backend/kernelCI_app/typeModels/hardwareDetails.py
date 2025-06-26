from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings

from kernelCI_app.typeModels.commonDetails import (
    BuildHistoryItem,
    GlobalFilters,
    LocalFilters,
    Summary,
    TestHistoryItem,
)

from kernelCI_app.typeModels.databases import (
    Issue__Id,
    Origin,
    StatusValues,
    Checkout__TreeName,
    Checkout__GitRepositoryBranch,
    Issue__Version,
)
from pydantic import BaseModel, BeforeValidator, Field


def process_status(value: Any) -> Any:
    if value is None:
        return "NULL"
    return value


class DefaultRecordValues(BaseModel):
    status: Annotated[StatusValues, BeforeValidator(process_status)]


class HardwareDetailsPostBody(BaseModel):
    origin: str = Field(
        default=DEFAULT_ORIGIN,
        description=DocStrings.HARDWARE_DETAILS_ORIGIN_DESCRIPTION,
    )
    startTimestampInSeconds: Union[str, int] = Field(  # noqa: N815
        description=DocStrings.DEFAULT_START_TS_DESCRIPTION
    )
    endTimestampInSeconds: Union[str, int] = Field(  # noqa: N815
        description=DocStrings.DEFAULT_END_TS_DESCRIPTION
    )
    selectedCommits: Dict[str, str] = Field(  # noqa: N815
        description=DocStrings.HARDWARE_DETAILS_SEL_COMMITS_DESCRIPTION
    )
    filter: Optional[Dict] = Field(
        None,
        description=DocStrings.DEFAULT_FILTER_DESCRIPTION,
    )


class CommitHead(BaseModel):
    treeName: str  # noqa: N815
    repositoryUrl: str  # noqa: N815
    branch: str  # noqa: N815
    commitHash: str  # noqa: N815


class CommitHistoryPostBody(BaseModel):
    origin: str = Field(default="maestro")
    startTimestampInSeconds: Union[str, int]  # noqa: N815
    endTimestampInSeconds: Union[str, int]  # noqa: N815
    commitHeads: List[CommitHead]  # noqa: N815


class CommitHistoryValidCheckout(BaseModel):
    git_commit_hash: str
    tree_name: str
    git_repository_branch: str
    git_repository_url: str
    git_commit_tags: Optional[List[str]] = []
    git_commit_name: Optional[str]
    start_time: datetime


class Tree(BaseModel):
    index: str
    origin: Origin
    tree_name: Optional[str]
    git_repository_branch: Optional[str]
    git_repository_url: Optional[str]
    head_git_commit_name: Optional[str]
    head_git_commit_hash: Optional[str]
    head_git_commit_tag: Optional[List[str]]
    selected_commit_status: Optional[Dict]
    is_selected: Optional[bool]


class HardwareCommon(BaseModel):
    trees: List[Tree]
    compatibles: List[str]


class HardwareTestLocalFilters(LocalFilters):
    platforms: List[str]


class HardwareDetailsFilters(BaseModel):
    all: GlobalFilters
    builds: LocalFilters
    boots: HardwareTestLocalFilters
    tests: HardwareTestLocalFilters


class HardwareTestHistoryItem(TestHistoryItem):
    tree_name: Checkout__TreeName
    git_repository_branch: Checkout__GitRepositoryBranch


class HardwareBuildHistoryItem(BuildHistoryItem):
    tree_name: Checkout__TreeName
    issue_id: Optional[Issue__Id]
    issue_version: Optional[Issue__Version]


class HardwareDetailsFullResponse(BaseModel):
    builds: List[HardwareBuildHistoryItem]
    boots: List[HardwareTestHistoryItem]
    tests: List[HardwareTestHistoryItem]
    summary: Summary
    filters: HardwareDetailsFilters
    common: HardwareCommon


class HardwareDetailsSummaryResponse(BaseModel):
    summary: Summary
    filters: HardwareDetailsFilters
    common: HardwareCommon


class HardwareDetailsBuildsResponse(BaseModel):
    builds: List[HardwareBuildHistoryItem]


class HardwareDetailsBootsResponse(BaseModel):
    boots: List[HardwareTestHistoryItem]


class HardwareDetailsTestsResponse(BaseModel):
    tests: List[HardwareTestHistoryItem]


class HardwareCommitHistoryResponse(BaseModel):
    commit_history_table: Dict[str, List[CommitHistoryValidCheckout]]

    class Config:
        # TODO: Implement this modification (additionalProp{n} -> commit_hash_{n}) dynamically
        json_schema_extra = {
            "example": {
                "commit_history_table": {
                    "commit_hash_1": [
                        {
                            "git_commit_hash": "string",
                            "tree_name": "string",
                            "git_repository_branch": "string",
                            "git_repository_url": "string",
                            "git_commit_tags": ["string"],
                            "git_commit_name": "string",
                            "start_time": "datetime",
                        }
                    ],
                    "commit_hash_2": [
                        {
                            "git_commit_hash": "string",
                            "tree_name": "string",
                            "git_repository_branch": "string",
                            "git_repository_url": "string",
                            "git_commit_tags": ["string"],
                            "git_commit_name": "string",
                            "start_time": "datetime",
                        }
                    ],
                    "commit_hash_3": [
                        {
                            "git_commit_hash": "string",
                            "tree_name": "string",
                            "git_repository_branch": "string",
                            "git_repository_url": "string",
                            "git_commit_tags": ["string"],
                            "git_commit_name": "string",
                            "start_time": "datetime",
                        }
                    ],
                }
            }
        }


type PossibleTestType = Literal["test", "boot"]
