from typing import Annotated
from pydantic import BaseModel, BeforeValidator, Field

from kernelCI_app.constants.general import DEFAULT_INTERVAL_IN_DAYS, DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings


class ListingInterval(BaseModel):
    interval_in_days: Annotated[
        int,
        Field(
            default=DEFAULT_INTERVAL_IN_DAYS,
            gt=0,
            description=DocStrings.DEFAULT_INTERVAL_DESCRIPTION,
        ),
    ]


class ListingQueryParameters(ListingInterval):
    origin: Annotated[
        str,
        Field(
            default=DEFAULT_ORIGIN,
            description=DocStrings.LISTING_QUERY_ORIGIN_DESCRIPTION,
        ),
        BeforeValidator(lambda o: DEFAULT_ORIGIN if o is None else o),
    ]
