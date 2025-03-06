from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.test import get_test_details_data, get_test_status_history
from kernelCI_app.typeModels.databases import FAIL_STATUS, PASS_STATUS
from kernelCI_app.typeModels.testDetails import (
    PossibleRegressionType,
    TestDetailsResponse,
)
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError


class TestDetails(APIView):
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
        responses=TestDetailsResponse,
    )
    def get(self, _request, test_id: str) -> Response:

        response = get_test_details_data(test_id=test_id)

        if response is None:
            return create_api_error_response(
                error_message="Test not found", status_code=HTTPStatus.OK
            )

        platform = response["environment_misc"].get("platform")

        status_history_response = get_test_status_history(
            path=response["path"],
            origin=response["build__checkout__origin"],
            git_repository_url=response["build__checkout__git_repository_url"],
            git_repository_branch=response["build__checkout__git_repository_branch"],
            platform=platform,
            current_test_timestamp=response["field_timestamp"],
        )

        regression_type = self.process_test_status_history(
            status_history=status_history_response
        )

        try:
            valid_response = TestDetailsResponse(
                **response,
                status_history=status_history_response,
                regression_type=regression_type,
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
