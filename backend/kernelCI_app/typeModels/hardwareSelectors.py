from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings


class HardwareSelectorRevision(BaseModel):
    git_commit_hash: str
    git_commit_name: str | None = None
    start_time: datetime


class HardwareSelectorBranch(BaseModel):
    git_repository_url: str
    git_repository_branch: str
    revisions: list[HardwareSelectorRevision]


class HardwareSelectorTree(BaseModel):
    tree_name: str
    branches: list[HardwareSelectorBranch]


class HardwareSelectorsResponse(BaseModel):
    trees: list[HardwareSelectorTree]


class HardwareSelectorsQueryParamsDocumentationOnly(BaseModel):
    origin: Annotated[
        str,
        Field(
            default=DEFAULT_ORIGIN,
            description=DocStrings.HARDWARE_LISTING_ORIGIN_DESCRIPTION,
        ),
    ]


class HardwareSelectorsQueryParams(BaseModel):
    origin: Annotated[
        str,
        Field(default=DEFAULT_ORIGIN),
        BeforeValidator(lambda o: DEFAULT_ORIGIN if o is None else o),
    ]
