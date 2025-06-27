from drf_spectacular.utils import OpenApiParameter

COMMIT_HASH_PATH_PARAM_REQUIRED = OpenApiParameter(
    name="commit_hash",
    description="Commit hash of the tree",
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

TREE_NAME_PATH_PARAM_REQUIRED = OpenApiParameter(
    name="tree_name",
    description="Name of the tree",
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

GIT_BRANCH_PATH_PARAM_REQUIRED = OpenApiParameter(
    name="git_branch",
    description="Branch name of the tree",
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

BUILD_ID_PATH_PARAM_REQUIRED = OpenApiParameter(
    name="build_id",
    description="ID of the build to retrieve issues",
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

HARDWARE_ID_PATH_PARAM_REQUIRED = OpenApiParameter(
    name="hardware_id",
    description="ID of the hardware, as the name of the platform/compatible",
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

ISSUE_ID_PATH_PARAM_REQUIRED = OpenApiParameter(
    name="issue_id",
    description="ID of the issue",
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)

TEST_ID_PATH_PARAM_REQUIRED = OpenApiParameter(
    name="test_id",
    description="ID of the test",
    required=True,
    type=str,
    location=OpenApiParameter.PATH,
)
