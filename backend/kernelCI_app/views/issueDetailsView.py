from http import HTTPStatus
from typing import Dict, Optional
from django.http import JsonResponse
from django.views import View
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.models import Issues
from kernelCI_app.typeModels.issueDetails import IssueDetailsPathParameters
from pydantic import ValidationError


class IssueDetails(View):
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
            "build_valid",
            "test_status",
            "comment",
            "misc",
        ]

        query = (
            Issues.objects.values(*issue_fields)
            .filter(id=issue_id, version=version)
            .first()
        )

        return query

    def get(self, _request, issue_id: Optional[str], version: Optional[str]) -> JsonResponse:
        try:
            parsed_params = IssueDetailsPathParameters(
                issue_id=issue_id, version=version
            )
        except ValidationError as e:
            return create_error_response(e.json())

        issue_data = self._fetch_issue(
            issue_id=parsed_params.issue_id, version=parsed_params.version
        )

        if not issue_data:
            return create_error_response(
                error_message="Issue not found", status_code=HTTPStatus.NOT_FOUND
            )

        return JsonResponse(issue_data)
