from http import HTTPStatus
from typing import Optional
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.queries.issues import get_issue_details, get_latest_issue_version
from kernelCI_app.typeModels.issueDetails import (
    IssueDetailsPathParameters,
    IssueDetailsQueryParameters,
    IssueDetailsResponse,
)
from kernelCI_app.helpers.issueExtras import process_issues_extra_details
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from pydantic import ValidationError


class IssueDetails(APIView):
    def __init__(self):
        self.processed_issue_extras = {}

    @extend_schema(
        parameters=[IssueDetailsQueryParameters],
        responses=IssueDetailsResponse,
        methods=["GET"],
    )
    def get(self, _request, issue_id: Optional[str]) -> Response:
        try:
            path_params = IssueDetailsPathParameters(issue_id=issue_id)
            query_params = IssueDetailsQueryParameters(
                version=_request.GET.get("version")
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        if query_params.version is None:
            version_row = get_latest_issue_version(issue_id=path_params.issue_id)
            if version_row is None:
                return create_api_error_response(
                    error_message="Issue not found", status_code=HTTPStatus.OK
                )
            query_params.version = version_row["version"]

        issue_data = get_issue_details(
            issue_id=path_params.issue_id, version=query_params.version
        )

        if not issue_data:
            return create_api_error_response(
                error_message="Issue not found", status_code=HTTPStatus.OK
            )

        process_issues_extra_details(
            issue_key_list=[(issue_id, query_params.version)],
            processed_issues_table=self.processed_issue_extras,
        )

        try:
            valid_response = IssueDetailsResponse(
                **issue_data, extra=self.processed_issue_extras
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=valid_response.model_dump())
