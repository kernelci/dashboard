from http import HTTPStatus
from urllib.parse import urlencode
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import JsonResponse
from django.urls import reverse
from pydantic import ValidationError

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.trees import get_tree_file_data, get_tree_url_to_name_map
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
    def get(self, request, tree_name: str, branch: str) -> JsonResponse:
        try:
            parsed_params = TreeLatestPathParameters(tree_name=tree_name, branch=branch)
        except ValidationError as e:
            return Response(data=e.json, status=HTTPStatus.BAD_REQUEST)

        tree_not_found_error_message = "Tree not found."
        origin = request.GET.get("origin")
        if origin is None:
            origin = DEFAULT_ORIGIN
            tree_not_found_error_message += (
                f" No origin was provided so it was defaulted to {DEFAULT_ORIGIN}"
            )
        git_commit_hash = request.GET.get("git_commit_hash")

        defined_url = None
        trees_from_file = get_tree_file_data().get("trees")
        if trees_from_file is not None:
            defined_url = trees_from_file.get(tree_name, {}).get("url")

        if defined_url is not None:
            tree_data = get_latest_tree(
                branch=parsed_params.branch,
                origin=origin,
                git_commit_hash=git_commit_hash,
                git_repository_url=defined_url,
            )
        else:
            tree_data = get_latest_tree(
                branch=parsed_params.branch,
                origin=origin,
                git_commit_hash=git_commit_hash,
                tree_name=parsed_params.tree_name,
            )

        if tree_data is None:
            return create_api_error_response(
                error_message=tree_not_found_error_message,
                status_code=HTTPStatus.OK,
            )

        # Since the priority is now the tree name from the yaml file,
        # if a tree had a name A in kcidb but it has name B on the file,
        # searching for the name A will return with its name replaced
        tree_url_to_name = get_tree_url_to_name_map()
        defined_tree_name = tree_url_to_name.get(
            tree_data["git_repository_url"], tree_data["tree_name"]
        )
        tree_data["tree_name"] = defined_tree_name

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
            "git_branch": branch,
        }
        query_string = f"?{urlencode(query_params)}"

        response_data = {**tree_data, "api_url": f"{base_url}{query_string}"}

        try:
            valid_response = TreeLatestResponse(**response_data)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
