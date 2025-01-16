from http import HTTPStatus
from typing import Dict, Optional
from django.http import JsonResponse
from django.views import View
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.models import Incidents
from kernelCI_app.typeModels.issueDetails import IssueDetailsPathParameters
from pydantic import ValidationError


class IssueDetailsTests(View):
    def _fetch_incidents(self, *, issue_id: str, version: int) -> Optional[Dict]:
        fields = [
            "test__id",
            "test__duration",
            "test__status",
            "test__path",
            "test__start_time",
            "test__environment_compatible",
        ]

        tests = Incidents.objects.filter(
            issue_id=issue_id, issue_version=version
        ).values(*fields)

        return [
            {
                "id": test["test__id"],
                "duration": test["test__duration"],
                "status": test["test__status"],
                "path": test["test__path"],
                "start_time": test["test__start_time"],
                "environment_compatible": test["test__environment_compatible"],
            }
            for test in tests
        ]

    def get(
        self, _request, issue_id: Optional[str], version: Optional[str]
    ) -> JsonResponse:
        try:
            parsed_params = IssueDetailsPathParameters(
                issue_id=issue_id, version=version
            )
        except ValidationError as e:
            return create_error_response(e.json())

        tests_data = self._fetch_incidents(
            issue_id=parsed_params.issue_id, version=parsed_params.version
        )

        if not tests_data:
            return create_error_response(
                error_message="Tests not found", status_code=HTTPStatus.NOT_FOUND
            )

        return JsonResponse(tests_data, safe=False)
