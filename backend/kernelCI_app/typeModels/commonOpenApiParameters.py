from drf_spectacular.utils import OpenApiParameter
from kernelCI_app.constants.localization import DocStrings

COMMIT_HASH_PATH_PARAM = OpenApiParameter(
    name="commit_hash",
    description=DocStrings.COMMIT_HASH_PATH_DESCRIPTION,
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

TREE_NAME_PATH_PARAM = OpenApiParameter(
    name="tree_name",
    description=DocStrings.TREE_NAME_PATH_DESCRIPTION,
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

GIT_BRANCH_PATH_PARAM = OpenApiParameter(
    name="git_branch",
    description=DocStrings.DEFAULT_GIT_BRANCH_DESCRIPTION,
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

BUILD_ID_PATH_PARAM = OpenApiParameter(
    name="build_id",
    description=DocStrings.BUILD_ID_PATH_DESCRIPTION,
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

HARDWARE_ID_PATH_PARAM = OpenApiParameter(
    name="hardware_id",
    description=DocStrings.HARDWARE_ID_PATH_DESCRIPTION,
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

ISSUE_ID_PATH_PARAM = OpenApiParameter(
    name="issue_id",
    description=DocStrings.ISSUE_ID_PATH_DESCRIPTION,
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

TEST_ID_PATH_PARAM = OpenApiParameter(
    name="test_id",
    description=DocStrings.TEST_ID_PATH_DESCRIPTION,
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

URL_QUERY_PARAM = OpenApiParameter(
    name="url",
    description=DocStrings.PROXY_URL_DESCRIPTION,
    required=True,
    type=str,
    location=OpenApiParameter.QUERY,
)
