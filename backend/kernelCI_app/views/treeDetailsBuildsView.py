from http import HTTPStatus
from typing import Optional

from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.discordWebhook import send_discord_notification
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.filters import (
    FilterParams,
)
from kernelCI_app.helpers.logger import create_endpoint_notification
from kernelCI_app.queries.treeBuilds import get_tree_builds_response
from kernelCI_app.typeModels.commonOpenApiParameters import (
    COMMIT_HASH_PATH_PARAM,
    GIT_BRANCH_PATH_PARAM,
    TREE_NAME_PATH_PARAM,
)
from kernelCI_app.typeModels.treeDetails import (
    DirectTreeQueryParameters,
    TreeDetailsBuildsResponse,
    TreeQueryParameters,
)


class BaseTreeDetailsBuilds(APIView):
    def get(
        self,
        request: HttpRequest,
        git_url: Optional[str],
        tree_name: Optional[str],
        git_branch: str,
        commit_hash: str,
        origin: str,
    ) -> Response:
        try:
            response = get_tree_builds_response(
                filters=FilterParams(request),
                origin=origin,
                git_url=git_url,
                git_branch=git_branch,
                tree_name=tree_name,
                commit_hash=commit_hash,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if response.get("error") == ClientStrings.TREE_BUILDS_NO_RESULTS:
            notification = create_endpoint_notification(
                message="Found checkout without builds", request=request
            )
            send_discord_notification(content=notification)
        return Response(response)


class TreeDetailsBuildsDirect(BaseTreeDetailsBuilds):
    @extend_schema(
        parameters=[
            TREE_NAME_PATH_PARAM,
            GIT_BRANCH_PATH_PARAM,
            COMMIT_HASH_PATH_PARAM,
            DirectTreeQueryParameters,
        ],
        methods=["GET"],
        responses=TreeDetailsBuildsResponse,
    )
    def get(
        self,
        request: HttpRequest,
        tree_name: str,
        git_branch: str,
        commit_hash: str,
    ) -> Response:
        try:
            params = DirectTreeQueryParameters.model_validate(request.GET.dict())
        except ValidationError as e:
            return create_api_error_response(error_message=e.json())

        return super().get(
            request=request,
            git_url=None,
            tree_name=tree_name,
            git_branch=git_branch,
            commit_hash=commit_hash,
            origin=params.origin,
        )


class TreeDetailsBuilds(BaseTreeDetailsBuilds):
    @extend_schema(
        parameters=[
            COMMIT_HASH_PATH_PARAM,
            TreeQueryParameters,
        ],
        methods=["GET"],
        responses=TreeDetailsBuildsResponse,
    )
    def get(
        self,
        request: HttpRequest,
        commit_hash: str,
    ) -> Response:
        try:
            params = TreeQueryParameters.model_validate(request.GET.dict())
        except ValidationError as e:
            return create_api_error_response(error_message=e.json())

        return super().get(
            request=request,
            git_url=params.git_url,
            tree_name=None,
            git_branch=params.git_branch,
            commit_hash=commit_hash,
            origin=params.origin,
        )
