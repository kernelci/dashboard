from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.typeModels.hardwareListing import _normalize_comma_list


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
    buildOrigin: Optional[str] = Field(  # noqa: N815
        default=DEFAULT_ORIGIN,
        description="Optional origin of builds that provide revisions",
    )
    origin: Optional[str] = Field(
        default=None,
        deprecated=True,
        description="Deprecated alias for buildOrigin",
    )


class HardwareSelectorsQueryParams(BaseModel):
    build_origin: Optional[list[str]] = Field(default_factory=lambda: [DEFAULT_ORIGIN])

    @classmethod
    def from_request(cls, query):
        raw = query.get("buildOrigin", query.get("origin", DEFAULT_ORIGIN))
        return cls(build_origin=_normalize_comma_list(raw))
