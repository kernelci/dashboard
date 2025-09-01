from typing import Optional
from pydantic import BaseModel, Field
from kernelCI_app.constants.localization import DocStrings

from kernelCI_app.typeModels.commonListing import ListingInterval
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


class IssueListingQueryParameters(ListingInterval):
    filter: dict[str, str] = Field(
        None,
        description=DocStrings.DEFAULT_FILTER_DESCRIPTION,
    )
    starting_date_iso_format: Optional[str] = Field(
        None,
        description=DocStrings.DEFAULT_LISTING_STARTING_DATE_DESCRIPTION,
    )


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
