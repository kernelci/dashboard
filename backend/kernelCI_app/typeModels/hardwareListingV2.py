from datetime import datetime
from pydantic import BaseModel, BeforeValidator, Field
from typing import Annotated, Optional, Union

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings


class StatusCountV2(BaseModel):
    PASS: Optional[int] = 0
    FAIL: Optional[int] = 0
    INCONCLUSIVE: Optional[int] = 0


class HardwareItemV2(BaseModel):
    hardware: Optional[Union[str, set[str]]]
    platform: str
    test_status_summary: StatusCountV2
    boot_status_summary: StatusCountV2
    build_status_summary: StatusCountV2


class HardwareListingResponseV2(BaseModel):
    hardware: list[HardwareItemV2]


class HardwareQueryParamsV2DocumentationOnly(BaseModel):
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


class HardwareQueryParamsV2(BaseModel):
    origin: Annotated[
        str,
        Field(default=DEFAULT_ORIGIN),
        BeforeValidator(lambda o: DEFAULT_ORIGIN if o is None else o),
    ]
    start_date: datetime
    end_date: datetime
