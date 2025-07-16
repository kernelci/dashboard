from pydantic import BaseModel, Field

from kernelCI.settings import DEFAULT_ORIGIN_LISTING_INTERVAL_IN_DAYS
from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.databases import Origin


class OriginsQueryParameters(BaseModel):
    interval_in_days: int = Field(
        default=DEFAULT_ORIGIN_LISTING_INTERVAL_IN_DAYS,
        gt=0,
        description=DocStrings.DEFAULT_INTERVAL_DESCRIPTION,
    )


class OriginsResponse(BaseModel):
    checkout_origins: list[Origin]
    test_origins: list[Origin]
