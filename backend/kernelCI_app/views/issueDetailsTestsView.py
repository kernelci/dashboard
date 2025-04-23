from http import HTTPStatus
from typing import Optional

from django.http import HttpRequest
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.issues import get_issue_tests
from kernelCI_app.typeModels.issueDetails import (
    IssueDetailsPathParameters,
    IssueDetailsQueryParameters,
    IssueTestsResponse,
)
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from pydantic import ValidationError


class IssueDetailsTests(APIView):
    @extend_schema(
        parameters=[IssueDetailsQueryParameters],
        responses=IssueTestsResponse,
        methods=["GET"],
    )
    def get(self, _request: HttpRequest, issue_id: Optional[str]) -> Response:
        try:
            path_params = IssueDetailsPathParameters(issue_id=issue_id)
            query_params = IssueDetailsQueryParameters(
                version=_request.GET.get("version")
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        tests_data = get_issue_tests(
            issue_id=path_params.issue_id, version=query_params.version
        )

        if not tests_data:
            return create_api_error_response(
                error_message="No tests found for this issue", status_code=HTTPStatus.OK
            )

        try:
            valid_response = IssueTestsResponse(tests_data)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=valid_response.model_dump())
