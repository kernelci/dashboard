from http import HTTPStatus
from typing import Dict, Optional
from kernelCI_app.models import Incidents
from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from kernelCI_app.helpers.issueDetails import fetch_latest_issue_version
from kernelCI_app.typeModels.issueDetails import (
    IssueBuildsResponse,
    IssueDetailsPathParameters,
    IssueDetailsQueryParameters,
)
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from pydantic import ValidationError


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
            "build__checkout__tree_name",
            "build__checkout__git_repository_branch",
        ]

        return Incidents.objects.filter(
            issue_id=issue_id, issue_version=version
        ).values(*fields)

    @extend_schema(
        parameters=[IssueDetailsQueryParameters],
        responses=IssueBuildsResponse,
        methods=["GET"],
    )
    def get(self, _request, issue_id: Optional[str]) -> Response:
        try:
            version = _request.GET.get("version")
            parsed_params = IssueDetailsPathParameters(issue_id=issue_id)
            parsed_query = IssueDetailsQueryParameters(version=version)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.BAD_REQUEST)

        if parsed_query.version is None:
            version_row = fetch_latest_issue_version(issue_id=parsed_params.issue_id)
            if version_row is None:
                return create_api_error_response(
                    error_message="Issue not found", status_code=HTTPStatus.OK
                )
            parsed_query.version = version_row["version"]

        builds_data = self._fetch_incidents(
            issue_id=parsed_params.issue_id, version=parsed_query.version
        )

        if not builds_data:
            return create_api_error_response(
                error_message="No builds found for this issue",
                status_code=HTTPStatus.OK,
            )

        try:
            valid_response = IssueBuildsResponse(builds_data)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(data=valid_response.model_dump())
