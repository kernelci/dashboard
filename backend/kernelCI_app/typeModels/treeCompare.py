from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings

CompareGroupedStatus = Literal["PASS", "FAIL", "INCONCLUSIVE"]


class CompareStatusCounts(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pass_count: int = Field(alias="pass", default=0)
    fail_count: int = Field(alias="fail", default=0)
    inconclusive: int = 0


class CompareDelta(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pass_count: int = Field(alias="pass", default=0)
    fail_count: int = Field(alias="fail", default=0)


class CompareChangeCounts(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    regression: int = 0
    fixed: int = 0
    new_failure: int = Field(alias="newFailure", default=0)
    still_failing: int = Field(alias="stillFailing", default=0)
    new_pass: int = Field(alias="newPass", default=0)
    appeared: int = 0
    disappeared: int = 0


class CompareEntitySummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    side_a: CompareStatusCounts = Field(alias="sideA")
    side_b: CompareStatusCounts = Field(alias="sideB")
    delta: CompareDelta
    changes: CompareChangeCounts = Field(default_factory=CompareChangeCounts)


class CompareSummary(BaseModel):
    builds: CompareEntitySummary
    boots: CompareEntitySummary
    tests: CompareEntitySummary


class TreeCompareResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tree_name: str = Field(alias="treeName")
    branch: str
    git_url: str = Field(alias="gitUrl", default="")
    summary: CompareSummary


class TreeCompareQueryParameters(BaseModel):
    hash_a: str = Field(description="Commit hash for side A")
    hash_b: str = Field(description="Commit hash for side B")
    origin: str = Field(
        default=DEFAULT_ORIGIN,
        description=DocStrings.TREE_QUERY_ORIGIN_DESCRIPTION,
    )


class CompareBuildDiffRow(BaseModel):
    config_name: str
    architecture: str
    compiler: str
    status_a: Optional[CompareGroupedStatus] = None
    status_b: Optional[CompareGroupedStatus] = None
    id_a: Optional[str] = None
    id_b: Optional[str] = None


class TreeCompareBuildsResponse(RootModel[List[CompareBuildDiffRow]]):
    root: List[CompareBuildDiffRow]
