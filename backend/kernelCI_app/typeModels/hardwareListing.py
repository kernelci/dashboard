from datetime import datetime
from typing import Annotated, Optional, Union

from pydantic import BaseModel, BeforeValidator, Field

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


class HardwareFiltersResponse(BaseModel):
    """Values available for each hardware listing filter."""

    checkout_origins: list[str]
    build_origins: list[str]
    build_labs: list[str]
    test_origins: list[str]
    test_labs: list[str]


class HardwareFiltersQueryParams(BaseModel):
    start_date: datetime
    end_date: datetime


class HardwareListingByRevisionResponse(BaseModel):
    hardware: list[HardwareItem]


# Since OpenAPI does not support timestamp as datetime we add an extra model just for
# documentation purposes. This model is not used in the code.
# TODO Remove timestamp from the api and this model
class HardwareQueryParamsDocumentationOnly(BaseModel):
    origin: Annotated[
        Optional[str],
        Field(
            default=None,
            description=DocStrings.HARDWARE_LISTING_DEPRECATED_ORIGIN_DESCRIPTION,
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
    checkoutOrigin: Optional[str] = Field(  # noqa: N815
        default=None,
        description=DocStrings.HARDWARE_LISTING_CHECKOUT_ORIGIN_DESCRIPTION,
    )
    buildOrigin: Optional[str] = Field(  # noqa: N815
        default=None,
        description=DocStrings.HARDWARE_LISTING_BUILD_ORIGIN_DESCRIPTION,
    )
    testOrigin: Optional[str] = Field(  # noqa: N815
        default=None,
        description=DocStrings.HARDWARE_LISTING_TEST_ORIGIN_DESCRIPTION,
    )
    buildLab: Optional[str] = Field(  # noqa: N815
        default=None,
        description=DocStrings.HARDWARE_LISTING_BUILD_LAB_DESCRIPTION,
    )
    testLab: Optional[str] = Field(  # noqa: N815
        default=None,
        description=DocStrings.HARDWARE_LISTING_TEST_LAB_DESCRIPTION,
    )


class HardwareFiltersQueryParamsDocumentationOnly(BaseModel):
    startTimestampInSeconds: str = Field(  # noqa: N815
        description=DocStrings.DEFAULT_START_TS_DESCRIPTION
    )
    endTimestampInSeconds: str = Field(  # noqa: N815
        description=DocStrings.DEFAULT_END_TS_DESCRIPTION
    )


class HardwareQueryParams(BaseModel):
    start_date: datetime
    end_date: datetime
    commits_list: Annotated[
        Optional[list[str]],
        BeforeValidator(_normalize_commits_list),
    ] = Field(default=None)
    # All five filters are optional and unset means unfiltered. Callers choose their own
    # defaults, so that a user can ask for every test origin instead of just the default one.
    checkout_origin: Optional[str] = None
    build_origin: Optional[str] = None
    build_lab: Optional[str] = None
    test_origin: Optional[str] = None
    test_lab: Optional[str] = None
