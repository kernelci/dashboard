from datetime import datetime
from typing import Annotated, Optional, Union

from pydantic import BaseModel, BeforeValidator, Field

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.commonListing import ListingStatusCount


def _normalize_comma_list(value: object) -> Optional[list[str]]:
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

    @classmethod
    def from_row(cls, row: tuple) -> "HardwareListingItem":
        return cls(
            platform=row[0],
            hardware=row[1],
            build_status_summary=ListingStatusCount(
                PASS=row[2], FAIL=row[3], INCONCLUSIVE=row[4]
            ),
            boot_status_summary=ListingStatusCount(
                PASS=row[5], FAIL=row[6], INCONCLUSIVE=row[7]
            ),
            test_status_summary=ListingStatusCount(
                PASS=row[8], FAIL=row[9], INCONCLUSIVE=row[10]
            ),
        )


class HardwareListingResponse(BaseModel):
    hardware: list[HardwareListingItem]


class HardwareFiltersResponse(BaseModel):
    checkout_origins: list[str]
    build_origins: list[str]
    test_origins: list[str]
    build_labs: list[str]
    test_labs: list[str]


class HardwareFiltersQueryParams(BaseModel):
    start_date: datetime
    end_date: datetime


class HardwareFiltersQueryParamsDocumentationOnly(BaseModel):
    startTimestampInSeconds: str = Field(  # noqa: N815
        description=DocStrings.DEFAULT_START_TS_DESCRIPTION
    )
    endTimestampInSeconds: str = Field(  # noqa: N815
        description=DocStrings.DEFAULT_END_TS_DESCRIPTION
    )


class HardwareFilterParams(BaseModel):
    """Side-specific origin/lab filters; empty clears to all. `origin` aliases checkout+build only."""

    checkout_origin: Optional[list[str]] = Field(
        default_factory=lambda: [DEFAULT_ORIGIN]
    )
    build_origin: Optional[list[str]] = Field(default_factory=lambda: [DEFAULT_ORIGIN])
    test_origin: Optional[list[str]] = None
    build_lab: Optional[list[str]] = None
    test_lab: Optional[list[str]] = None

    @classmethod
    def from_request(cls, query, **extra):
        origin_default = query.get("origin", DEFAULT_ORIGIN)

        def parse(name: str, fallback: Optional[str]) -> Optional[list[str]]:
            raw = query.get(name)
            if raw is None:
                raw = fallback
            return _normalize_comma_list(raw)

        return cls(
            checkout_origin=parse("checkoutOrigin", origin_default),
            build_origin=parse("buildOrigin", origin_default),
            test_origin=parse("testOrigin", None),
            build_lab=parse("buildLab", None),
            test_lab=parse("testLab", None),
            **extra,
        )


# Since OpenAPI does not support timestamp as datetime we add an extra model just for
# documentation purposes. This model is not used in the code.
# TODO Remove timestamp from the api and this model
class HardwareQueryParamsDocumentationOnly(BaseModel):
    checkoutOrigin: Annotated[  # noqa: N815
        Optional[str],
        Field(
            default=DEFAULT_ORIGIN,
            description=DocStrings.HARDWARE_LISTING_ORIGIN_DESCRIPTION,
        ),
    ]
    buildOrigin: Optional[str] = DEFAULT_ORIGIN  # noqa: N815
    testOrigin: Optional[str] = None  # noqa: N815
    buildLab: Optional[str] = None  # noqa: N815
    testLab: Optional[str] = None  # noqa: N815
    origin: Optional[str] = Field(
        default=None,
        deprecated=True,
        description="Deprecated alias for checkoutOrigin and buildOrigin",
    )
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


class HardwareQueryParams(HardwareFilterParams):
    start_date: datetime
    end_date: datetime
    commits_list: Annotated[
        Optional[list[str]],
        BeforeValidator(_normalize_comma_list),
    ] = Field(default=None)
