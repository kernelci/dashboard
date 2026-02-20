from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, RootModel, field_validator

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.treeListing import TestStatusCount
from pydantic import Field
from kernelCI_app.typeModels.databases import (
    Checkout__GitCommitHash,
    Checkout__GitCommitName,
    Checkout__GitCommitTags,
)


class TreeEntityTypes(str, Enum):
    BUILDS = "builds"
    BOOTS = "boots"
    TESTS = "tests"


class DirectTreeCommitsQueryParameters(BaseModel):
    origin: str = Field(
        DEFAULT_ORIGIN, description=DocStrings.TREE_COMMIT_ORIGIN_DESCRIPTION
    )
    start_timestamp_in_seconds: Optional[str] = Field(
        None, description=DocStrings.TREE_COMMIT_START_TS_DESCRIPTION
    )
    end_timestamp_in_seconds: Optional[str] = Field(
        None, description=DocStrings.TREE_COMMIT_END_TS_DESCRIPTION
    )
    types: Optional[list[TreeEntityTypes]] = Field(
        None,
        description="List of types to include (builds, boots, tests)",
    )
    builds_related_to_filtered_tests_only: bool = Field(
        False,
        description=(
            "When true, and requesting only builds, count only builds related to "
            "tests/boots that pass the current filters."
        ),
    )
    # TODO: Add filters field in this model

    @field_validator("types", mode="before")
    @classmethod
    def validate_types(cls, value):
        if not value:
            return []
        if isinstance(value, str):
            value = [t.strip() for t in value.split(",") if t.strip()]
        return value


class TreeCommitsQueryParameters(DirectTreeCommitsQueryParameters):
    git_branch: Optional[str] = Field(
        description=DocStrings.TREE_COMMIT_GIT_BRANCH_DESCRIPTION
    )
    git_url: Optional[str] = Field(
        description=DocStrings.TREE_COMMIT_GIT_URL_DESCRIPTION
    )


class TreeCommitsData(BaseModel):
    git_commit_hash: Checkout__GitCommitHash
    git_commit_name: Checkout__GitCommitName
    git_commit_tags: Checkout__GitCommitTags
    earliest_start_time: datetime
    builds: StatusCount
    boots: TestStatusCount
    tests: TestStatusCount


class TreeCommitsResponse(RootModel):
    root: List[TreeCommitsData]
