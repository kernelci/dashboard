from typing import Dict, Optional, Tuple
from pydantic import BaseModel


class IncidentInfo(BaseModel):
    incidentsCount: int


class Issue(BaseModel):
    id: str
    version: int
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentInfo


type IssueDict = Dict[Tuple[str, str], Issue]
