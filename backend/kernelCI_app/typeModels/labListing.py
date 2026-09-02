from pydantic import BaseModel

from kernelCI_app.typeModels.commonListing import ListingStatusCount


class LabListingItem(BaseModel):
    lab_name: str
    build_status_summary: ListingStatusCount
    boot_status_summary: ListingStatusCount
    test_status_summary: ListingStatusCount


class LabListingResponse(BaseModel):
    labs: list[LabListingItem]
