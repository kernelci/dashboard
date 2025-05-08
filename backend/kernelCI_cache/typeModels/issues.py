from pydantic import BaseModel
from kernelCI_app.typeModels.databases import Issue__Id, Issue__Version
from kernelCI_cache.typeModels.databases import PossibleIssueType


class IssueKeyTuple(BaseModel):
    root: tuple[Issue__Id, Issue__Version]


class UnsentIssueKeys(BaseModel):
    issue_id: Issue__Id
    issue_version: Issue__Version
    issue_type: PossibleIssueType
