from http import HTTPStatus
from typing import Dict, Optional
from django.http import JsonResponse
from django.views import View
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.models import Incidents
from kernelCI_app.typeModels.issueDetails import IssueDetailsPathParameters
from pydantic import ValidationError


class IssueDetailsBuilds(View):
    def _fetch_incidents(self, *, issue_id: str, version: int) -> Optional[Dict]:
        fields = [
            "build__id",
            "build__architecture",
            "build__config_name",
            "build__valid",
            "build__start_time",
            "build__duration",
            "build__compiler",
            "build__log_url",
        ]

        builds = Incidents.objects.filter(
            issue_id=issue_id, issue_version=version
        ).values(*fields)

        return [
            {
                "id": build["build__id"],
                "architecture": build["build__architecture"],
                "config_name": build["build__config_name"],
                "valid": build["build__valid"],
                "start_time": build["build__start_time"],
                "duration": build["build__duration"],
                "compiler": build["build__compiler"],
                "log_url": build["build__log_url"],
            }
            for build in builds
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

        builds_data = self._fetch_incidents(
            issue_id=parsed_params.issue_id, version=parsed_params.version
        )

        if not builds_data:
            return create_error_response(
                error_message="Builds not found", status_code=HTTPStatus.NOT_FOUND
            )

        return JsonResponse(builds_data, safe=False)
