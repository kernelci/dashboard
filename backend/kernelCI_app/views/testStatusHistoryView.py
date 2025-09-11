from http import HTTPStatus

from django.http import HttpRequest
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.test import process_test_status_history
from kernelCI_app.queries.test import get_test_status_history
from kernelCI_app.typeModels.testDetails import (
    TestStatusHistoryRequest,
    TestStatusHistoryResponse,
)
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError
from kernelCI_app.constants.localization import ClientStrings


class TestStatusHistory(APIView):
    @extend_schema(
        parameters=[TestStatusHistoryRequest],
        request=TestStatusHistoryRequest,
        responses=TestStatusHistoryResponse,
    )
    def get(self, request: HttpRequest) -> Response:
        try:
            params = TestStatusHistoryRequest.model_validate(request.GET.dict())
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
            group_size=params.group_size,
        )

        if len(status_history_response) == 0:
            # This endpoint should always return at least 1 item (the current test),
            # if the result has no items it means that the request was wrong
            return create_api_error_response(
                error_message=ClientStrings.TEST_STATUS_HISTORY_NOT_FOUND
            )

        regression_type = process_test_status_history(
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
