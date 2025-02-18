from pydantic import BaseModel

from kernelCI_app.typeModels.databases import (
    Issue__Comment,
    Issue__CulpritCode,
    Issue__CulpritHarness,
    Issue__CulpritTool,
    Issue__Id,
    Issue__Version,
    Timestamp,
)
from kernelCI_app.typeModels.issues import FirstIncident


class IssueListingItem(BaseModel):
    field_timestamp: Timestamp
    id: Issue__Id
    comment: Issue__Comment
    version: Issue__Version
    culprit_code: Issue__CulpritCode
    culprit_tool: Issue__CulpritTool
    culprit_harness: Issue__CulpritHarness


class IssueListingResponse(BaseModel):
    issues: list[IssueListingItem]
    extras: dict[str, FirstIncident]
