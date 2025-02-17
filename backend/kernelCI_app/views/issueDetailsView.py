from http import HTTPStatus
from typing import Dict, Optional
from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.helpers.issueDetails import fetch_latest_issue_version
from kernelCI_app.models import Issues
from kernelCI_app.typeModels.issueDetails import (
    IssueDetailsPathParameters,
    IssueDetailsRequest,
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

    # TODO: combine fetching latest version here
    def _fetch_issue(self, *, issue_id: str, version: int) -> Optional[Dict]:
        issue_fields = [
            "field_timestamp",
            "id",
            "version",
            "origin",
            "report_url",
            "report_subject",
            "culprit_code",
            "culprit_tool",
            "culprit_harness",
            "comment",
            "misc",
        ]

        query = (
            Issues.objects.values(*issue_fields)
            .filter(id=issue_id, version=version)
            .first()
        )

        return query

    @extend_schema(
        request=IssueDetailsRequest, responses=IssueDetailsResponse, methods=["GET"]
    )
    def get(self, _request, issue_id: Optional[str]) -> Response:
        try:
            parsed_params = IssueDetailsPathParameters(issue_id=issue_id)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        version = _request.GET.get("version")
        if version is None:
            version_row = fetch_latest_issue_version(issue_id=parsed_params.issue_id)
            if version_row is None:
                return create_api_error_response(
                    error_message="Issue not found", status_code=HTTPStatus.OK
                )
            version = version_row["version"]

        issue_data = self._fetch_issue(issue_id=parsed_params.issue_id, version=version)
        process_issues_extra_details(
            issue_key_list=[(issue_id, version)],
            processed_issues_table=self.processed_issue_extras,
        )

        if not issue_data:
            return create_api_error_response(
                error_message="Issue not found", status_code=HTTPStatus.OK
            )

        try:
            valid_response = IssueDetailsResponse(
                **issue_data, extra=self.processed_issue_extras
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=valid_response.model_dump())
