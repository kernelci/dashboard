from http import HTTPStatus

from django.http import HttpRequest
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.test import get_test_status_history
from kernelCI_app.typeModels.databases import FAIL_STATUS, PASS_STATUS
from kernelCI_app.typeModels.testDetails import (
    PossibleRegressionType,
    TestStatusHistoryRequest,
    TestStatusHistoryResponse,
)
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError


class TestStatusHistory(APIView):
    # TODO: create unit tests for this method
    def process_test_status_history(
        self, *, status_history: list[dict]
    ) -> PossibleRegressionType:
        history_task: PossibleRegressionType
        first_test_flag = True
        status_changed = False

        for test in status_history:
            test_status = test["status"]
            if first_test_flag:
                if test_status == PASS_STATUS:
                    history_task = "pass"
                    starting_status = PASS_STATUS
                    opposite_status = FAIL_STATUS
                elif test_status == FAIL_STATUS:
                    history_task = "fail"
                    starting_status = FAIL_STATUS
                    opposite_status = PASS_STATUS
                else:
                    return "unstable"
                first_test_flag = False
                continue

            is_inconclusive = test_status != PASS_STATUS and test_status != FAIL_STATUS

            if test_status == opposite_status:
                status_changed = True
                if history_task == "pass":
                    history_task = "fixed"
                elif history_task == "fail":
                    history_task = "regression"
            if (status_changed and test_status == starting_status) or is_inconclusive:
                return "unstable"

        return history_task

    @extend_schema(
        parameters=[TestStatusHistoryRequest],
        request=TestStatusHistoryRequest,
        responses=TestStatusHistoryResponse,
    )
    def get(self, request: HttpRequest) -> Response:
        try:
            params = TestStatusHistoryRequest(
                path=request.GET.get("path"),
                origin=request.GET.get("origin"),
                git_repository_branch=request.GET.get("git_repository_branch"),
                git_repository_url=request.GET.get("git_repository_url"),
                platform=request.GET.get("platform"),
                current_test_start_time=request.GET.get("current_test_start_time"),
                config_name=request.GET.get("config_name"),
                field_timestamp=request.GET.get("field_timestamp"),
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        status_history_response = get_test_status_history(
            path=params.path,
            origin=params.origin,
            git_repository_url=params.git_repository_url,
            git_repository_branch=params.git_repository_branch,
            platform=params.platform,
            test_start_time=params.current_test_start_time,
            config_name=params.config_name,
            field_timestamp=params.field_timestamp,
        )

        if len(status_history_response) == 0:
            # This endpoint should always return at least 1 item (the current test),
            # if the result has no items it means that the request was wrong
            return create_api_error_response(
                error_message="Test status history not found"
            )

        regression_type = self.process_test_status_history(
            status_history=status_history_response
        )

        try:
            valid_response = TestStatusHistoryResponse(
                status_history=status_history_response,
                regression_type=regression_type,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
