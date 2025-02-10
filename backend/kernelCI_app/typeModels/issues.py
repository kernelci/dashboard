from datetime import datetime
from typing import Dict, List, Literal, Optional, Set, Tuple
from pydantic import BaseModel


class IncidentInfo(BaseModel):
    incidentsCount: int


class IssueKeys(BaseModel):
    id: str
    version: int


class Issue(IssueKeys):
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentInfo


type IssueDict = Dict[Tuple[str, int], Issue]


type PossibleIssueTags = Literal["mainline", "stable", "linux-next"]


class TreeSetItem(BaseModel):
    tree_name: Optional[str]
    git_repository_branch: Optional[str]


class IssueWithExtraInfo(IssueKeys):
    first_seen: Optional[datetime] = None
    trees: Optional[List[TreeSetItem]] = []
    tags: Optional[Set[PossibleIssueTags]] = set()


class IssueExtraDetailsRequest(BaseModel):
    issues: List[Tuple[str, int]]


type ProcessedExtraDetailedIssues = Dict[str, Dict[int, IssueWithExtraInfo]]


class IssueExtraDetailsResponse(BaseModel):
    issues: ProcessedExtraDetailedIssues
