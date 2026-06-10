from datetime import datetime
from typing import Annotated, Optional, Union

from pydantic import BaseModel, BeforeValidator, Field

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.commonListing import ListingStatusCount


def _normalize_commits_list(value: object) -> Optional[list[str]]:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = [part.strip() for part in value.split(",") if part.strip()]
        return cleaned if cleaned else None
    return None


class HardwareItem(BaseModel):
    hardware: Optional[Union[str, set[str]]]
    platform: str
    test_status_summary: StatusCount
    boot_status_summary: StatusCount
    build_status_summary: StatusCount


class HardwareListingItem(BaseModel):
    hardware: Optional[Union[str, set[str]]]
    platform: str
    test_status_summary: ListingStatusCount
    boot_status_summary: ListingStatusCount
    build_status_summary: ListingStatusCount


class HardwareListingResponse(BaseModel):
    hardware: list[HardwareListingItem]


class HardwareListingByRevisionResponse(BaseModel):
    hardware: list[HardwareItem]


# Since OpenAPI does not support timestamp as datetime we add an extra model just for
# documentation purposes. This model is not used in the code.
# TODO Remove timestamp from the api and this model
class HardwareQueryParamsDocumentationOnly(BaseModel):
    origin: Annotated[
        str,
        Field(
            default=DEFAULT_ORIGIN,
            description=DocStrings.HARDWARE_LISTING_ORIGIN_DESCRIPTION,
        ),
    ]
    startTimestampInSeconds: str = Field(  # noqa: N815
        description=DocStrings.DEFAULT_START_TS_DESCRIPTION
    )
    endTimestampInSeconds: str = Field(  # noqa: N815
        description=DocStrings.DEFAULT_END_TS_DESCRIPTION
    )
    commitsList: Optional[str] = Field(  # noqa: N815
        default=None,
        description=DocStrings.HARDWARE_LISTING_COMMITS_LIST_DESCRIPTION,
    )


class HardwareQueryParams(BaseModel):
    origin: Annotated[
        str,
        Field(default=DEFAULT_ORIGIN),
        BeforeValidator(lambda o: DEFAULT_ORIGIN if o is None else o),
    ]
    start_date: datetime
    end_date: datetime
    commits_list: Annotated[
        Optional[list[str]],
        BeforeValidator(_normalize_commits_list),
    ] = Field(default=None)
