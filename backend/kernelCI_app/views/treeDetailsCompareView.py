from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.queries.tree import get_tree_compare_boots_tests_diff
from kernelCI_app.typeModels.commonOpenApiParameters import (
    GIT_BRANCH_PATH_PARAM,
    TREE_NAME_PATH_PARAM,
)
from kernelCI_app.typeModels.treeCompare import TreeCompareQueryParameters
from kernelCI_app.typeModels.treeDetails import TreeCompareBootsTestsResponse


class BaseTreeDetailsCompare(APIView):
    data_type: Literal["boots", "tests"]

    def get(
        self,
        request: HttpRequest,
        tree_name: str,
        git_branch: str,
    ) -> Response:
        try:
            params = TreeCompareQueryParameters(
                hash_a=request.GET.get("hash_a", ""),
                hash_b=request.GET.get("hash_b", ""),
                origin=request.GET.get("origin", DEFAULT_ORIGIN),
            )
        except ValidationError as e:
            return create_api_error_response(error_message=e.json())

        if not params.hash_a or not params.hash_b:
            return create_api_error_response(
                status_code=HTTPStatus.BAD_REQUEST,
                error_message="hash_a and hash_b are required",
            )

        filters = FilterParams(request)
        rows = get_tree_compare_boots_tests_diff(
            data_type=self.data_type,
            hash_a=params.hash_a,
            hash_b=params.hash_b,
            origin=params.origin,
            git_branch=git_branch,
            tree_name=tree_name,
            filters=filters,
            boots_duration=(
                filters.filterBootDurationMin,
                filters.filterBootDurationMax,
            ),
            tests_duration=(
                filters.filterTestDurationMin,
                filters.filterTestDurationMax,
            ),
        )

        try:
            response = TreeCompareBootsTestsResponse(root=rows)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(response.model_dump())


class TreeDetailsBootsCompare(BaseTreeDetailsCompare):
    data_type = "boots"

    @extend_schema(
        parameters=[
            TREE_NAME_PATH_PARAM,
            GIT_BRANCH_PATH_PARAM,
            TreeCompareQueryParameters,
        ],
        methods=["GET"],
        responses=TreeCompareBootsTestsResponse,
    )
    def get(
        self,
        request: HttpRequest,
        tree_name: str,
        git_branch: str,
    ) -> Response:
        return super().get(request, tree_name, git_branch)


class TreeDetailsTestsCompare(BaseTreeDetailsCompare):
    data_type = "tests"

    @extend_schema(
        parameters=[
            TREE_NAME_PATH_PARAM,
            GIT_BRANCH_PATH_PARAM,
            TreeCompareQueryParameters,
        ],
        methods=["GET"],
        responses=TreeCompareBootsTestsResponse,
    )
    def get(
        self,
        request: HttpRequest,
        tree_name: str,
        git_branch: str,
    ) -> Response:
        return super().get(request, tree_name, git_branch)
