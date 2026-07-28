from typing import Optional

from pydantic import BaseModel, Field

from kernelCI_app.constants.localization import DocStrings


class HardwareListingByRevisionQueryParamsDocumentationOnly(BaseModel):
    testOrigin: Optional[str] = Field(  # noqa: N815
        default=None,
        description=DocStrings.HARDWARE_LISTING_TEST_ORIGIN_DESCRIPTION,
    )
    origin: Optional[str] = Field(
        default=None,
        description=DocStrings.HARDWARE_LISTING_DEPRECATED_ORIGIN_DESCRIPTION,
    )
    tree_name: str = Field(description=DocStrings.TREE_NAME_PATH_DESCRIPTION)
    git_repository_url: str = Field(
        description=DocStrings.TREE_QUERY_GIT_URL_DESCRIPTION
    )
    git_repository_branch: str = Field(
        description=DocStrings.DEFAULT_GIT_BRANCH_DESCRIPTION
    )
    git_commit_hash: str = Field(description=DocStrings.COMMIT_HASH_PATH_DESCRIPTION)


class HardwareListingByRevisionQueryParams(BaseModel):
    # This listing only knows about the origin of the tests, and unset means every origin,
    # matching the listing it shares the page with
    test_origin: Optional[str] = None
    tree_name: str
    git_repository_url: str
    git_repository_branch: str
    git_commit_hash: str
