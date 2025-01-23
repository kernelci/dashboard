from typing import Dict, Tuple
from drf_spectacular.utils import extend_schema
from kernelCI_app.typeModels.issues import Issue
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.helpers.filters import (
    FilterParams,
)
from kernelCI_app.helpers.treeDetails import (
    decide_if_is_full_row_filtered_out,
    decide_if_is_test_filtered_out,
    get_current_row_data,
    get_tree_details_data,
    is_test_boots_test,
)
from kernelCI_app.typeModels.treeDetails import (
    TreeQueryParameters,
)
from kernelCI_app.typeModels.commonDetails import (
    CommonDetailsTestsResponse,
    TestHistoryItem,
)


type IssueDict = Dict[Tuple[str, str], Issue]


class TreeDetailsTests(APIView):
    def __init__(self):
        self.processedTests = set()
        self.filters = None

        self.testHistory = []

    def _process_non_boots_test(self, row_data):
        test_id = row_data["test_id"]
        history_item = row_data["history_item"]

        if decide_if_is_test_filtered_out(self, row_data):
            return

        if test_id in self.processedTests:
            return

        self.processedTests.add(test_id)

        TestHistoryItem(**history_item)

        self.testHistory.append(history_item)

    def _sanitize_rows(self, rows):
        for row in rows:
            row_data = get_current_row_data(row)

            is_record_filter_out = decide_if_is_full_row_filtered_out(self, row_data)

            if is_record_filter_out:
                continue

            if row_data["test_id"] is None:
                continue

            if is_test_boots_test(row_data):
                continue
            else:
                self._process_non_boots_test(row_data)

    @extend_schema(
        parameters=[TreeQueryParameters],
        responses=CommonDetailsTestsResponse,
    )
    def get(self, request, commit_hash: str | None):
        rows = get_tree_details_data(request, commit_hash)

        self.filters = FilterParams(request)

        if len(rows) == 0:
            return create_error_response(
                error_message="No tests found for this tree", status_code=HTTPStatus.OK
            )

        try:
            self._sanitize_rows(rows)

            valid_response = CommonDetailsTestsResponse(
                tests=self.testHistory,
            )
        except ValidationError as e:
            return Response(data=e.errors(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=valid_response.model_dump(), status=HTTPStatus.OK)
