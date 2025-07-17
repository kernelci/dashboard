from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.test import get_test_details_data
from kernelCI_app.typeModels.commonOpenApiParameters import TEST_ID_PATH_PARAM
from kernelCI_app.typeModels.testDetails import (
    TestDetailsResponse,
)
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError
from kernelCI_app.constants.localization import ClientStrings


class TestDetails(APIView):
    @extend_schema(
        parameters=[TEST_ID_PATH_PARAM],
        responses=TestDetailsResponse,
    )
    def get(self, _request, test_id: str) -> Response:
        response = get_test_details_data(test_id=test_id)

        if not response:
            return create_api_error_response(
                error_message=ClientStrings.TEST_NOT_FOUND, status_code=HTTPStatus.OK
            )

        try:
            valid_response = TestDetailsResponse(**response[0])
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
