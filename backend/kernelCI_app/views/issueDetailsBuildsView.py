from http import HTTPStatus
from typing import Dict, Optional
from kernelCI_app.models import Incidents
from kernelCI_app.typeModels.issues import (
    IssueDetailsPathParameters,
)
from kernelCI_app.typeModels.issueDetails import IssuesBuildResponse
from pydantic import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response


class IssueDetailsBuilds(APIView):
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

    @extend_schema(responses=IssuesBuildResponse)
    def get(
        self, _request, issue_id: Optional[str], version: Optional[str]
    ) -> Response:
        try:
            parsed_params = IssueDetailsPathParameters(
                issue_id=issue_id, version=version
            )
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        builds_data = self._fetch_incidents(
            issue_id=parsed_params.issue_id, version=parsed_params.version
        )

        if not builds_data:
            return Response(
                data={"error": "No builds found for this issue"},
                status=HTTPStatus.OK,
            )

        try:
            valid_response = IssuesBuildResponse(builds_data)
        except ValidationError as e:
            return Response(
                data=e.json(),
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return Response(valid_response.model_dump())
