from http import HTTPStatus

from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.queries.tree import get_tree_compare_builds_diff
from kernelCI_app.typeModels.commonOpenApiParameters import (
    GIT_BRANCH_PATH_PARAM,
    TREE_NAME_PATH_PARAM,
)
from kernelCI_app.typeModels.treeCompare import (
    TreeCompareBuildsResponse,
    TreeCompareQueryParameters,
)


class TreeCompareBuildsView(APIView):
    @extend_schema(
        parameters=[
            TREE_NAME_PATH_PARAM,
            GIT_BRANCH_PATH_PARAM,
            TreeCompareQueryParameters,
        ],
        responses=TreeCompareBuildsResponse,
    )
    def get(
        self,
        request: HttpRequest,
        tree_name: str,
        git_branch: str,
    ) -> Response:
        try:
            query_params = TreeCompareQueryParameters(
                hash_a=request.GET.get("hash_a", ""),
                hash_b=request.GET.get("hash_b", ""),
                origin=request.GET.get("origin", DEFAULT_ORIGIN),
            )
        except ValidationError as error:
            return Response(data=error.json(), status=HTTPStatus.BAD_REQUEST)

        if not query_params.hash_a or not query_params.hash_b:
            return create_api_error_response(
                status_code=HTTPStatus.BAD_REQUEST,
                error_message="hash_a and hash_b are required",
            )

        filters = FilterParams(request)
        rows = get_tree_compare_builds_diff(
            hash_a=query_params.hash_a,
            hash_b=query_params.hash_b,
            origin_param=query_params.origin,
            git_branch_param=git_branch,
            tree_name=tree_name,
            filters=filters,
        )

        try:
            response = TreeCompareBuildsResponse(root=rows)
        except ValidationError as error:
            return Response(
                data=error.json(),
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return Response(
            data=response.model_dump(),
            status=HTTPStatus.OK,
        )
