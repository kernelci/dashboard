from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.treeCompare import build_compare_rows, collapse_side_statuses
from kernelCI_app.queries.tree import get_tree_compare_data
from kernelCI_app.typeModels.commonOpenApiParameters import (
    GIT_BRANCH_PATH_PARAM,
    TREE_NAME_PATH_PARAM,
)
from kernelCI_app.typeModels.treeDetails import (
    TreeCompareQueryParameters,
    TreeCompareResponse,
)


class BaseTreeDetailsCompare(APIView):
    data_type: Literal["boots", "tests"]

    def get(
        self,
        request: HttpRequest,
        tree_name: str,
        git_branch: str,
    ) -> Response:
        try:
            params = TreeCompareQueryParameters.model_validate(request.GET.dict())
        except ValidationError as e:
            return create_api_error_response(error_message=e.json())

        filters = FilterParams(request)
        rows = get_tree_compare_data(
            data_type=self.data_type,
            origin=params.origin,
            git_branch=git_branch,
            tree_name=tree_name,
            commit_hashes=[params.commit_a, params.commit_b],
            boots_duration=(
                filters.filterBootDurationMin,
                filters.filterBootDurationMax,
            ),
            tests_duration=(
                filters.filterTestDurationMin,
                filters.filterTestDurationMax,
            ),
        )

        status_a, status_b = collapse_side_statuses(
            rows=rows,
            commit_a=params.commit_a,
            commit_b=params.commit_b,
            filters=filters,
            data_type=self.data_type,
        )

        try:
            response = TreeCompareResponse(
                root=build_compare_rows(status_a, status_b, full=params.full)
            )
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
        responses=TreeCompareResponse,
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
        responses=TreeCompareResponse,
    )
    def get(
        self,
        request: HttpRequest,
        tree_name: str,
        git_branch: str,
    ) -> Response:
        return super().get(request, tree_name, git_branch)
