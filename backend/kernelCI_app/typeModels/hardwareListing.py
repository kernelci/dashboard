from datetime import datetime
from pydantic import BaseModel, BeforeValidator, Field
from typing import Annotated, TypedDict

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.typeModels.databases import StatusValues


class BuildStatusCountDict(TypedDict):
    valid: int
    invalid: int
    null: int


class HardwareItem(BaseModel):
    hardware_name: str
    platform: str | set[str]
    test_status_summary: dict[StatusValues, int]
    boot_status_summary: dict[StatusValues, int]
    build_status_summary: BuildStatusCountDict


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
    endTimeStampInSeconds: str  # noqa: N815


class HardwareQueryParams(BaseModel):
    origin: Annotated[
        str,
        Field(default=DEFAULT_ORIGIN),
        BeforeValidator(lambda o: DEFAULT_ORIGIN if o is None else o),
    ]
    start_date: datetime
    end_date: datetime
