from http import HTTPStatus
from typing import Dict, Optional
from kernelCI_app.models import Incidents
from kernelCI_app.typeModels.issues import (
    IssueDetailsPathParameters,
)
from kernelCI_app.typeModels.issueDetails import IssuesTestsResponse
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from pydantic import ValidationError


class IssueDetailsTests(APIView):
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

    @extend_schema(responses=IssuesTestsResponse)
    def get(
        self, _request, issue_id: Optional[str], version: Optional[str]
    ) -> Response:
        try:
            parsed_params = IssueDetailsPathParameters(
                issue_id=issue_id, version=version
            )
        except ValidationError as e:
            return Response(
                data=e.json(),
                status=HTTPStatus.BAD_REQUEST,
            )

        tests_data = self._fetch_incidents(
            issue_id=parsed_params.issue_id, version=parsed_params.version
        )

        if not tests_data:
            return Response(
                data={"error": "No tests found for this issue"}, status=HTTPStatus.OK
            )

        try:
            valid_response = IssuesTestsResponse(tests_data)
        except ValidationError as e:
            return Response(
                data=e.json(),
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return Response(valid_response.model_dump())
