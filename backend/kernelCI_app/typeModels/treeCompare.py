from pydantic import BaseModel, ConfigDict, Field

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings


class CompareStatusCounts(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pass_count: int = Field(alias="pass", default=0)
    fail_count: int = Field(alias="fail", default=0)
    inconclusive: int = 0


class CompareDelta(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pass_count: int = Field(alias="pass", default=0)
    fail_count: int = Field(alias="fail", default=0)


class CompareEntitySummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    side_a: CompareStatusCounts = Field(alias="sideA")
    side_b: CompareStatusCounts = Field(alias="sideB")
    delta: CompareDelta


class CompareGroupRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    label: str
    side_a: CompareStatusCounts = Field(alias="sideA")
    side_b: CompareStatusCounts = Field(alias="sideB")
    delta: CompareDelta


class CompareSummary(BaseModel):
    builds: CompareEntitySummary
    boots: CompareEntitySummary
    tests: CompareEntitySummary


class CompareGroups(BaseModel):
    builds: list[CompareGroupRow]
    boots: list[CompareGroupRow]
    tests: list[CompareGroupRow]


class TreeCompareResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tree_name: str = Field(alias="treeName")
    branch: str
    git_url: str = Field(alias="gitUrl", default="")
    summary: CompareSummary
    groups: CompareGroups


class TreeCompareQueryParameters(BaseModel):
    hash_a: str = Field(description="Commit hash for side A")
    hash_b: str = Field(description="Commit hash for side B")
    origin: str = Field(
        default=DEFAULT_ORIGIN,
        description=DocStrings.TREE_QUERY_ORIGIN_DESCRIPTION,
    )
