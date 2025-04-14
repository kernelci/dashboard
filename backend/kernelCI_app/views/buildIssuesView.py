from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError

from kernelCI_app.helpers.detailsIssues import sanitize_details_issues_rows
from kernelCI_app.helpers.errorHandling import create_api_error_response
from http import HTTPStatus
from kernelCI_app.queries.issues import get_build_issues
from kernelCI_app.typeModels.detailsIssuesView import DetailsIssuesResponse


class BuildIssuesView(APIView):
    @extend_schema(responses=DetailsIssuesResponse)
    def get(
        self,
        _request,
        build_id: str,
    ) -> Response:
        records = get_build_issues(build_id=build_id)
        build_issues = sanitize_details_issues_rows(rows=records)

        if len(build_issues) == 0:
            return create_api_error_response(
                error_message="No issues were found for this build",
                status_code=HTTPStatus.OK,
            )

        try:
            valid_build_response = DetailsIssuesResponse(build_issues)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_build_response.model_dump())
