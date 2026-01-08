from typing import Annotated, Optional
from pydantic import BaseModel, Field

from kernelCI_app.constants.general import DEFAULT_INTERVAL_IN_DAYS, DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.common import make_default_validator


class ListingInterval(BaseModel):
    interval_in_days: Annotated[
        int,
        Field(
            default=DEFAULT_INTERVAL_IN_DAYS,
            gt=0,
            description=DocStrings.DEFAULT_INTERVAL_DESCRIPTION,
        ),
        make_default_validator(DEFAULT_INTERVAL_IN_DAYS),
    ]


class ListingQueryParameters(ListingInterval):
    origin: Annotated[
        str,
        Field(
            default=DEFAULT_ORIGIN,
            description=DocStrings.LISTING_QUERY_ORIGIN_DESCRIPTION,
        ),
        make_default_validator(DEFAULT_ORIGIN),
    ]


class StatusCountV2(BaseModel):
    PASS: Optional[int] = 0
    FAIL: Optional[int] = 0
    INCONCLUSIVE: Optional[int] = 0
