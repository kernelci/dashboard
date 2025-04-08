from http import HTTPStatus
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.trees import get_tree_url_to_name_map
from kernelCI_app.queries.test import get_test_details_data
from kernelCI_app.typeModels.testDetails import (
    TestDetailsResponse,
)
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError


class TestDetails(APIView):
    @extend_schema(
        responses=TestDetailsResponse,
    )
    def get(self, _request, test_id: str) -> Response:
        response = get_test_details_data(test_id=test_id)

        if not response:
            return create_api_error_response(
                error_message="Test not found", status_code=HTTPStatus.OK
            )

        tree_url_to_name = get_tree_url_to_name_map()
        defined_name = tree_url_to_name.get(
            response[0]["git_repository_url"], response[0]["tree_name"]
        )
        response[0]["tree_name"] = defined_name

        try:
            valid_response = TestDetailsResponse(**response[0])
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_response.model_dump())
