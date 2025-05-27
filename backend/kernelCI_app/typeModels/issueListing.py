from pydantic import BaseModel
from kernelCI_app.typeModels.commonListing import ListingQueryParameters

from kernelCI_app.typeModels.databases import (
    Issue__Categories,
    Issue__Comment,
    Issue__CulpritCode,
    Issue__CulpritHarness,
    Issue__CulpritTool,
    Issue__Id,
    Issue__Version,
    Timestamp,
    Origin,
)
from kernelCI_app.typeModels.issues import FirstIncident


class IssueListingQueryParameters(ListingQueryParameters):
    culprit_code: bool | None = False
    culprit_harness: bool | None = False
    culprit_tool: bool | None = False


class IssueListingItem(BaseModel):
    field_timestamp: Timestamp
    id: Issue__Id
    comment: Issue__Comment
    origin: Origin
    version: Issue__Version
    culprit_code: Issue__CulpritCode
    culprit_tool: Issue__CulpritTool
    culprit_harness: Issue__CulpritHarness
    categories: Issue__Categories


class IssueListingFilters(BaseModel):
    origins: list[str]
    culprits: list[str]
    categories: list[str]


class IssueListingResponse(BaseModel):
    issues: list[IssueListingItem]
    extras: dict[str, FirstIncident]
    filters: IssueListingFilters
