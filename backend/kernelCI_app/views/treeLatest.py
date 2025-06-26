from http import HTTPStatus
from typing import Optional
from urllib.parse import urlencode
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import JsonResponse
from django.urls import reverse
from pydantic import ValidationError

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.tree import get_latest_tree
from kernelCI_app.typeModels.treeDetails import (
    TreeLatestPathParameters,
    TreeLatestResponse,
    TreeLatestQueryParameters,
)


class TreeLatest(APIView):
    @extend_schema(
        responses=TreeLatestResponse,
        parameters=[TreeLatestQueryParameters],
        methods=["GET"],
    )
    def get(
        self,
        request,
        tree_name: str,
        git_branch: str,
        commit_hash: Optional[str] = None,
    ) -> JsonResponse:
        try:
            parsed_params = TreeLatestPathParameters(
                tree_name=tree_name, git_branch=git_branch, commit_hash=commit_hash
            )
        except ValidationError as e:
            return Response(data=e.json, status=HTTPStatus.BAD_REQUEST)

        tree_not_found_error_message = "Tree not found."
        origin = request.GET.get("origin")
        if origin is None:
            origin = DEFAULT_ORIGIN
            tree_not_found_error_message += (
                f" No origin was provided so it was defaulted to {DEFAULT_ORIGIN}"
            )

        tree_data = get_latest_tree(
            tree_name=parsed_params.tree_name,
            git_branch=parsed_params.git_branch,
            origin=origin,
            git_commit_hash=parsed_params.commit_hash,
        )

        if tree_data is None:
            return create_api_error_response(
                error_message=tree_not_found_error_message,
                status_code=HTTPStatus.OK,
            )

        base_url = reverse(
            "treeDetailsView",
            kwargs={"commit_hash": tree_data["git_commit_hash"]},
        )

        # TODO: Newer versions of django added (or will add) a parameter to `reverse`
        # to pass the query parameters directly to it.
        # You can see more here: https://github.com/django/django/pull/18848
        # and here: https://code.djangoproject.com/ticket/25582#no1
        query_params = {
            "origin": origin,
            "git_url": tree_data["git_repository_url"],
            "git_branch": git_branch,
        }
        query_string = f"?{urlencode(query_params)}"

        response_data = {**tree_data, "api_url": f"{base_url}{query_string}"}

        try:
            valid_response = TreeLatestResponse(**response_data)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
