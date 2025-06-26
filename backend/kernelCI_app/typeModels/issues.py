from typing import Dict, List, Literal, Optional, Set, Tuple, Annotated
from pydantic import BaseModel, Field

from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.databases import (
    Timestamp,
    Checkout__GitCommitHash,
    Checkout__GitRepositoryUrl,
    Checkout__GitRepositoryBranch,
    Checkout__GitCommitName,
    Checkout__TreeName,
)


class IncidentInfo(BaseModel):
    incidentsCount: int  # noqa: N815


class IssueKeys(BaseModel):
    id: str
    version: int


class Issue(IssueKeys):
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: StatusCount


type IssueDict = Dict[Tuple[str, int], Issue]


type PossibleIssueTags = Literal["mainline", "stable", "linux-next"]


class TreeSetItem(BaseModel):
    tree_name: Optional[str]
    git_repository_branch: Optional[str]


class IssueWithExtraInfo(IssueKeys):
    trees: Optional[List[TreeSetItem]] = []
    tags: Optional[Set[PossibleIssueTags]] = set()


class IssueExtraDetailsRequest(BaseModel):
    issues: List[Tuple[str, int]] = Field(
        description=DocStrings.ISSUE_EXTRA_ID_LIST_DESCRIPTION
    )


class FirstIncident(BaseModel):
    first_seen: Timestamp
    git_commit_hash: Optional[Checkout__GitCommitHash]
    git_repository_url: Optional[Checkout__GitRepositoryUrl]
    git_repository_branch: Optional[Checkout__GitRepositoryBranch]
    git_commit_name: Optional[Checkout__GitCommitName]
    tree_name: Optional[Checkout__TreeName]


class ExtraIssuesData(BaseModel):
    first_incident: FirstIncident
    versions: Dict[int, IssueWithExtraInfo]


type ProcessedExtraDetailedIssues = Annotated[
    Dict[str, ExtraIssuesData],
    Field(
        description="Extra info about issues, grouped by ID when it's version-agnostic",
        examples=[
            (
                "redhat:issue_3332: { first_incident: { first_seen: '2024-10-20', "
                "git_commit_hash: 'commit1', git_repository_url: 'example.com', "
                "git_repository_branch: 'branch1'}, 0: {...}}"
            )
        ],
    ),
]


class IssueExtraDetailsResponse(BaseModel):
    issues: ProcessedExtraDetailedIssues


CULPRIT_CODE = "code"
CULPRIT_HARNESS = "harness"
CULPRIT_TOOL = "tool"

POSSIBLE_CULPRITS = [CULPRIT_CODE, CULPRIT_HARNESS, CULPRIT_TOOL]

type PossibleIssueCulprits = Literal["code", "harness", "tool"]


HAS_INCIDENT_OPTION = "hasIncident"

ISSUE_FILTER_OPTIONS = [HAS_INCIDENT_OPTION]
type IssueFilterOptions = Literal["hasIncident"]
