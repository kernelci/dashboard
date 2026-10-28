from http import HTTPStatus
from typing import Optional

from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.filters import (
    FilterParams,
)
from kernelCI_app.queries.treeTestHistory import get_tree_test_history_response
from kernelCI_app.typeModels.commonDetails import (
    CommonDetailsBootsResponse,
)
from kernelCI_app.typeModels.commonOpenApiParameters import (
    COMMIT_HASH_PATH_PARAM,
    GIT_BRANCH_PATH_PARAM,
    TREE_NAME_PATH_PARAM,
)
from kernelCI_app.typeModels.treeDetails import (
    DirectTreeDetailsQueryParameters,
    TreeDetailsQueryParameters,
)


class BaseTreeDetailsBoots(APIView):
    def get(
        self,
        request: HttpRequest,
        git_url: Optional[str],
        tree_name: Optional[str],
        git_branch: str,
        commit_hash: str,
        origin: str,
        full_environment_misc: bool = False,
    ) -> Response:
        try:
            response = get_tree_test_history_response(
                data_type="boots",
                filters=FilterParams(request),
                origin=origin,
                git_url=git_url,
                git_branch=git_branch,
                tree_name=tree_name,
                commit_hash=commit_hash,
                full_environment_misc=full_environment_misc,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response(response)


class TreeDetailsBootsDirect(BaseTreeDetailsBoots):
    @extend_schema(
        parameters=[
            TREE_NAME_PATH_PARAM,
            GIT_BRANCH_PATH_PARAM,
            COMMIT_HASH_PATH_PARAM,
            DirectTreeDetailsQueryParameters,
        ],
        methods=["GET"],
        responses=CommonDetailsBootsResponse,
    )
    def get(
        self,
        request: HttpRequest,
        tree_name: str,
        git_branch: str,
        commit_hash: str,
    ) -> Response:
        try:
            params = DirectTreeDetailsQueryParameters.model_validate(request.GET.dict())
        except ValidationError as e:
            return create_api_error_response(error_message=e.json())

        return super().get(
            request=request,
            git_url=None,
            tree_name=tree_name,
            git_branch=git_branch,
            commit_hash=commit_hash,
            origin=params.origin,
            full_environment_misc=params.full_environment_misc,
        )


class TreeDetailsBoots(BaseTreeDetailsBoots):
    @extend_schema(
        parameters=[
            COMMIT_HASH_PATH_PARAM,
            TreeDetailsQueryParameters,
        ],
        methods=["GET"],
        responses=CommonDetailsBootsResponse,
    )
    def get(
        self,
        request: HttpRequest,
        commit_hash: str,
    ) -> Response:
        try:
            params = TreeDetailsQueryParameters.model_validate(request.GET.dict())
        except ValidationError as e:
            return create_api_error_response(error_message=e.json())

        return super().get(
            request=request,
            git_url=params.git_url,
            tree_name=None,
            git_branch=params.git_branch,
            commit_hash=commit_hash,
            origin=params.origin,
            full_environment_misc=params.full_environment_misc,
        )
