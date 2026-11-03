from typing import Optional

from pydantic import BaseModel, Field

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings
from kernelCI_app.typeModels.hardwareListing import HardwareFilterParams


class HardwareListingByRevisionQueryParamsDocumentationOnly(BaseModel):
    checkoutOrigin: Optional[str] = DEFAULT_ORIGIN  # noqa: N815
    buildOrigin: Optional[str] = DEFAULT_ORIGIN  # noqa: N815
    testOrigin: Optional[str] = None  # noqa: N815
    buildLab: Optional[str] = None  # noqa: N815
    testLab: Optional[str] = None  # noqa: N815
    origin: Optional[str] = Field(
        default=None,
        deprecated=True,
        description="Deprecated alias for checkoutOrigin and buildOrigin",
    )
    tree_name: str = Field(description=DocStrings.TREE_NAME_PATH_DESCRIPTION)
    git_repository_url: str = Field(
        description=DocStrings.TREE_QUERY_GIT_URL_DESCRIPTION
    )
    git_repository_branch: str = Field(
        description=DocStrings.DEFAULT_GIT_BRANCH_DESCRIPTION
    )
    git_commit_hash: str = Field(description=DocStrings.COMMIT_HASH_PATH_DESCRIPTION)


class HardwareListingByRevisionQueryParams(HardwareFilterParams):
    tree_name: str
    git_repository_url: str
    git_repository_branch: str
    git_commit_hash: str
