from pydantic import BaseModel


class IssueDetailsPathParameters(BaseModel):
    issue_id: str
    version: int
