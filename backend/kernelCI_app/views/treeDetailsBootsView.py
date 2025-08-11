from http import HTTPStatus
from typing import Optional

from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.filters import (
    FilterParams,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from kernelCI_app.helpers.treeDetails import (
    decide_if_is_boot_filtered_out,
    decide_if_is_full_row_filtered_out,
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
    TreeQueryParameters,
)
from kernelCI_app.typeModels.commonDetails import (
    CommonDetailsBootsResponse,
    TestHistoryItem,
)
from kernelCI_app.utils import is_boot


class BaseTreeDetailsBoots(APIView):
    def __init__(self):
        self.processedTests = set()
        self.filters = None
        self.bootHistory = []

    def _process_boots_test(self, row_data):
        test_id = row_data["test_id"]
        history_item = row_data["history_item"]

        if decide_if_is_boot_filtered_out(self, row_data):
            return

        if test_id in self.processedTests:
            return
        self.processedTests.add(test_id)
        TestHistoryItem(**history_item)
        self.bootHistory.append(history_item)

    def _sanitize_rows(self, rows):
        for row in rows:
            row_data = get_current_row_data(row)

            is_record_filter_out = decide_if_is_full_row_filtered_out(self, row_data)

            if is_record_filter_out:
                continue

            if row_data["test_id"] is None:
                continue

            if is_boot(row_data["test_path"]):
                self._process_boots_test(row_data)

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
            if row_data["test_id"] is None:
                return create_api_error_response(
                    error_message=ClientStrings.TREE_BOOTS_NO_RESULTS,
                    status_code=HTTPStatus.OK,
                )

        try:
            self._sanitize_rows(rows)

            valid_response = CommonDetailsBootsResponse(
                boots=self.bootHistory,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())


class TreeDetailsBootsDirect(BaseTreeDetailsBoots):
    @extend_schema(
        parameters=[
            TREE_NAME_PATH_PARAM,
            GIT_BRANCH_PATH_PARAM,
            COMMIT_HASH_PATH_PARAM,
            DirectTreeQueryParameters,
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


class TreeDetailsBoots(BaseTreeDetailsBoots):
    @extend_schema(
        parameters=[
            COMMIT_HASH_PATH_PARAM,
            TreeQueryParameters,
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
