from typing import Annotated
from pydantic import BaseModel, BeforeValidator, Field

from kernelCI_app.constants.general import DEFAULT_INTERVAL_IN_DAYS, DEFAULT_ORIGIN


class ListingQueryParameters(BaseModel):
    origin: Annotated[
        str,
        Field(default=DEFAULT_ORIGIN),
        BeforeValidator(lambda o: DEFAULT_ORIGIN if o is None else o),
    ]
    interval_in_days: Annotated[
        int,
        Field(default=DEFAULT_INTERVAL_IN_DAYS, gt=0),
        BeforeValidator(lambda i: DEFAULT_INTERVAL_IN_DAYS if i is None else i),
    ]
