from http import HTTPStatus
from typing import Optional
from kernelCI_app.helpers.errorHandling import (
    create_api_error_response,
)
from kernelCI_app.typeModels.commonOpenApiParameters import ISSUE_ID_PATH_PARAM
from kernelCI_app.typeModels.issueDetails import (
    IssueBuildsResponse,
    IssueDetailsPathParameters,
    IssueDetailsQueryParameters,
)
from kernelCI_app.queries.issues import get_issue_builds
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from pydantic import ValidationError


class IssueDetailsBuilds(APIView):
    @extend_schema(
        parameters=[
            ISSUE_ID_PATH_PARAM,
            IssueDetailsQueryParameters,
        ],
        responses=IssueBuildsResponse,
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

        builds_data = get_issue_builds(
            issue_id=path_params.issue_id, version=query_params.version
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
