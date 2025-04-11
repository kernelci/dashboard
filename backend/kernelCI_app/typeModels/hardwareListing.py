from datetime import datetime
from pydantic import BaseModel, BeforeValidator, Field
from typing import Annotated

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.typeModels.common import StatusCount


class HardwareItem(BaseModel):
    hardware_name: str
    platform: str | set[str]
    test_status_summary: StatusCount
    boot_status_summary: StatusCount
    build_status_summary: StatusCount


class HardwareResponse(BaseModel):
    hardware: list[HardwareItem]


# Since OpenAPI does not support timestamp as datetime we add an extra model just for
# documentation purposes. This model is not used in the code.
# TODO Remove timestamp from the api and this model
class HardwareQueryParamsDocumentationOnly(BaseModel):
    origin: Annotated[
        str,
        Field(default=DEFAULT_ORIGIN),
    ]
    startTimestampInSeconds: str  # noqa: N815
    endTimestampInSeconds: str  # noqa: N815


class HardwareQueryParams(BaseModel):
    origin: Annotated[
        str,
        Field(default=DEFAULT_ORIGIN),
        BeforeValidator(lambda o: DEFAULT_ORIGIN if o is None else o),
    ]
    start_date: datetime
    end_date: datetime
