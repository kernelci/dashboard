from http import HTTPStatus

from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.tree import get_tree_commits
from kernelCI_app.typeModels.treeCommits import (
    TreeCommitsListQueryParameters,
    TreeCommitsListResponse,
)


class TreeCommitsListView(APIView):
    @extend_schema(
        parameters=[TreeCommitsListQueryParameters],
        responses=TreeCommitsListResponse,
    )
    def get(self, request: HttpRequest, tree_name: str, git_branch: str) -> Response:

        try:
            query_params = TreeCommitsListQueryParameters(
                origin=request.GET.get("origin"),
                git_url=request.GET.get("git_url"),
            )
        except ValidationError:
            return create_api_error_response(
                status_code=HTTPStatus.BAD_REQUEST,
                error_message=ClientStrings.TREE_COMMITS_HISTORY_NOT_FOUND,
            )

        commits = get_tree_commits(
            origin=query_params.origin,
            tree_name=tree_name,
            git_branch=git_branch,
            git_url=query_params.git_url,
        )

        if not commits:
            return create_api_error_response(
                status_code=HTTPStatus.OK,
                error_message=ClientStrings.TREE_COMMITS_HISTORY_NOT_FOUND,
            )

        result = TreeCommitsListResponse(root=commits)

        return Response(data=result.model_dump(), status=HTTPStatus.OK)
