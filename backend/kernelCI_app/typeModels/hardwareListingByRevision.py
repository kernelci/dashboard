from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.constants.localization import DocStrings


class HardwareListingByRevisionQueryParamsDocumentationOnly(BaseModel):
    origin: Annotated[
        str,
        Field(
            default=DEFAULT_ORIGIN,
            description=DocStrings.HARDWARE_LISTING_ORIGIN_DESCRIPTION,
        ),
    ]
    tree_name: str = Field(description=DocStrings.TREE_NAME_PATH_DESCRIPTION)
    git_repository_url: str = Field(
        description=DocStrings.TREE_QUERY_GIT_URL_DESCRIPTION
    )
    git_repository_branch: str = Field(
        description=DocStrings.DEFAULT_GIT_BRANCH_DESCRIPTION
    )
    git_commit_hash: str = Field(description=DocStrings.COMMIT_HASH_PATH_DESCRIPTION)


class HardwareListingByRevisionQueryParams(BaseModel):
    origin: Annotated[
        str,
        Field(default=DEFAULT_ORIGIN),
        BeforeValidator(lambda o: DEFAULT_ORIGIN if o is None else o),
    ]
    tree_name: str
    git_repository_url: str
    git_repository_branch: str
    git_commit_hash: str
