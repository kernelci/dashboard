from typing import Dict, Optional
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.views import View
from kernelCI_app.models import Issues
from kernelCI_app.utils import getErrorResponseBody


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

    def get(self, _request, issue_id: Optional[str], version: Optional[str]):
        missing_params = []
        if issue_id is None:
            missing_params.append("issue_id")
        if version is None:
            missing_params.append("version")
        if len(missing_params) != 0:
            return HttpResponseBadRequest(
                getErrorResponseBody("Missing parameters: ", missing_params)
            )

        try:
            parsed_version = int(version)
        except ValueError:
            return HttpResponseBadRequest(
                getErrorResponseBody("Invalid version parameter, must be an integer")
            )

        issue_data = self._fetch_issue(issue_id=issue_id, version=parsed_version)

        if issue_data is None:
            return HttpResponseNotFound(getErrorResponseBody("Issue not found"))

        return JsonResponse(issue_data)
