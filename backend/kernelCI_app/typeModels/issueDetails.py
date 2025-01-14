from typing import Dict, Tuple
from kernelCI_app.utils import Issue
from pydantic import BaseModel


class IssueDetailsPathParameters(BaseModel):
    issue_id: str
    version: int


type IssueDict = Dict[Tuple[str, str], Issue]
