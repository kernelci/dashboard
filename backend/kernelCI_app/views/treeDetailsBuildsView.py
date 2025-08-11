from http import HTTPStatus
from typing import Dict, List, Optional
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
from kernelCI_app.helpers.treeDetails import (
    decide_if_is_build_filtered_out,
    decide_if_is_full_row_filtered_out,
    get_build,
    get_current_row_data,
)
from kernelCI_app.queries.tree import get_tree_details_data
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
from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX


class BaseTreeDetailsBuilds(APIView):
    def __init__(self):
        self.filters = None

        self.builds: List[Dict] = []
        self.processed_builds = set()
        self.tree_url = ""

    def _process_builds(self, row_data):
        build_id = row_data["build_id"]

        if decide_if_is_build_filtered_out(self, row_data):
            return

        if build_id in self.processed_builds:
            return

        self.processed_builds.add(build_id)

        build_item = get_build(row_data)

        self.builds.append(build_item)

    def _sanitize_rows(self, rows):
        for row in rows:
            row_data = get_current_row_data(row)

            is_record_filter_out = decide_if_is_full_row_filtered_out(self, row_data)

            if is_record_filter_out:
                continue

            if row_data["build_id"] is not None and not row_data["build_id"].startswith(
                MAESTRO_DUMMY_BUILD_PREFIX
            ):
                self._process_builds(row_data)

    def get(
        self,
        request: HttpRequest,
        git_url: Optional[str],
        tree_name: Optional[str],
        git_branch: str,
        commit_hash: str,
        origin: str,
    ) -> Response:
        rows = get_tree_details_data(
            origin_param=origin,
            git_url_param=git_url,
            git_branch_param=git_branch,
            tree_name=tree_name,
            commit_hash=commit_hash,
        )

        self.filters = FilterParams(request)

        if len(rows) == 0:
            return create_api_error_response(
                error_message=ClientStrings.TREE_NO_RESULTS,
                status_code=HTTPStatus.OK,
            )

        if len(rows) == 1:
            row_data = get_current_row_data(current_row=rows[0])
            if row_data["build_id"] is None:
                notification = create_endpoint_notification(
                    message="Found checkout without builds",
                    request=request,
                )
                send_discord_notification(content=notification)
                return create_api_error_response(
                    error_message=ClientStrings.TREE_BUILDS_NO_RESULTS,
                    status_code=HTTPStatus.OK,
                )

        self._sanitize_rows(rows)

        try:
            valid_response = TreeDetailsBuildsResponse(
                builds=self.builds,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())


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
