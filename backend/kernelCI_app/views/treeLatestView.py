from http import HTTPStatus
from urllib.parse import urlencode
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from pydantic import ValidationError

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.queries.tree import get_latest_tree
from kernelCI_app.typeModels.commonOpenApiParameters import (
    GIT_BRANCH_PATH_PARAM,
    TREE_NAME_PATH_PARAM,
)
from kernelCI_app.typeModels.treeDetails import (
    TreeLatestPathParameters,
    TreeLatestResponse,
    TreeLatestQueryParameters,
)
from kernelCI_app.constants.localization import ClientStrings


class TreeLatest(APIView):
    @extend_schema(
        responses=TreeLatestResponse,
        parameters=[
            TREE_NAME_PATH_PARAM,
            GIT_BRANCH_PATH_PARAM,
            TreeLatestQueryParameters,
        ],
        methods=["GET"],
    )
    def get(
        self,
        request: HttpRequest,
        tree_name: str,
        git_branch: str,
    ) -> JsonResponse:
        try:
            parsed_params = TreeLatestPathParameters(
                tree_name=tree_name, git_branch=git_branch
            )
            query_params = TreeLatestQueryParameters(**request.GET.dict())
        except ValidationError as e:
            return Response(data=e.json, status=HTTPStatus.BAD_REQUEST)

        origin = query_params.origin

        tree_data = get_latest_tree(
            tree_name=parsed_params.tree_name,
            git_branch=parsed_params.git_branch,
            origin=origin,
            git_commit_hash=query_params.commit_hash,
        )

        if tree_data is None:
            tree_not_found_error_message = ClientStrings.TREE_NOT_FOUND
            if request.GET.get("origin") is None:
                tree_not_found_error_message += (
                    f" {ClientStrings.TREE_LATEST_DEFAULT_ORIGIN} {DEFAULT_ORIGIN}"
                )

            params = parsed_params.model_dump()
            params.update(query_params.model_dump())

            return Response(
                data={"error": tree_not_found_error_message, "params": params},
                status=HTTPStatus.OK,
            )

        # The `old_api_url` is only used in the backend response in order to
        # keep compatibility with the full treeDetails endpoint in case someone
        # expects this format. It should be removed when we drop the support for the old format.
        # TODO: remove this field from the response.
        old_base_url = reverse(
            "treeDetailsView",
            kwargs={"commit_hash": tree_data["git_commit_hash"]},
        )
        old_query_params = {
            "origin": origin,
            "git_url": tree_data["git_repository_url"],
            "git_branch": git_branch,
        }
        old_query_string = f"?{urlencode(old_query_params)}"
        old_api_url = f"{old_base_url}{old_query_string}"

        # TODO: Newer versions of django (>5.2) added a parameter to `reverse`
        # to pass the query parameters directly to it.
        # You can see more here: https://github.com/django/django/pull/18848
        # and here: https://code.djangoproject.com/ticket/25582#no1
        base_url = reverse(
            "treeDetailsDirectView",
            kwargs={
                "tree_name": tree_data["tree_name"],
                "git_branch": tree_data["git_repository_branch"],
                "commit_hash": tree_data["git_commit_hash"],
            },
        )
        query_params = {
            "origin": origin,
        }
        query_string = f"?{urlencode(query_params)}"
        api_url = f"{base_url}{query_string}"

        try:
            valid_response = TreeLatestResponse(
                **tree_data,
                api_url=api_url,
                old_api_url=old_api_url,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
