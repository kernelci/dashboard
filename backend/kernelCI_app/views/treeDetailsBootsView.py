from typing import Dict, Tuple
from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from kernelCI_app.typeModels.issues import Issue
from pydantic import ValidationError
from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
    create_error_response,
)
from kernelCI_app.helpers.filters import (
    FilterParams,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from kernelCI_app.helpers.treeDetails import (
    decide_if_is_boot_filtered_out,
    decide_if_is_full_row_filtered_out,
    get_current_row_data,
    is_test_boots_test,
)
from kernelCI_app.queries.tree import get_tree_details_data
from kernelCI_app.typeModels.treeDetails import (
    TreeQueryParameters,
)
from kernelCI_app.typeModels.commonDetails import (
    CommonDetailsBootsResponse,
    TestHistoryItem,
)


type IssueDict = Dict[Tuple[str, str], Issue]


class TreeDetailsBoots(APIView):
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

            if is_test_boots_test(row_data):
                self._process_boots_test(row_data)

    @extend_schema(
        parameters=[TreeQueryParameters],
        methods=["GET"],
        responses=CommonDetailsBootsResponse,
    )
    def get(self, request, commit_hash: str | None):
        origin_param = request.GET.get("origin")
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch")

        rows = get_tree_details_data(
            origin_param, git_url_param, git_branch_param, commit_hash
        )

        self.filters = FilterParams(request)

        # Temporary during schema transition
        if rows is None:
            message = (
                "This error was probably caused because the server was using"
                "an old version of the database. Please try requesting again"
            )
            return create_api_error_response(
                error_message=message,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        if len(rows) == 0:
            return create_error_response(
                error_message="No boots found for this tree", status_code=HTTPStatus.OK
            )

        try:
            self._sanitize_rows(rows)

            valid_response = CommonDetailsBootsResponse(
                boots=self.bootHistory,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
