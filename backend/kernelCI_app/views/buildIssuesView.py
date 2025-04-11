from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError

from kernelCI_app.helpers.build import valid_status_field
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.helpers.detailsIssues import sanitize_details_issues_rows
from kernelCI_app.helpers.errorHandling import create_api_error_response
from http import HTTPStatus
from kernelCI_app.typeModels.issues import Issue
from kernelCI_app.typeModels.detailsIssuesView import DetailsIssuesResponse


class BuildIssuesView(APIView):
    def get_build_issues(self, build_id: str) -> list[Issue]:
        query = f"""
            SELECT
                incidents.id,
                issues.id,
                issues.version,
                issues.comment,
                issues.report_url,
                builds.{valid_status_field()} AS status
            FROM incidents
            JOIN issues
                ON incidents.issue_id = issues.id
                AND incidents.issue_version = issues.version
            JOIN builds
                ON incidents.build_id = builds.id
            WHERE incidents.build_id = %s
            """
        with connection.cursor() as cursor:
            cursor.execute(query, [build_id])
            rows = dict_fetchall(cursor=cursor)

        return rows

    @extend_schema(responses=DetailsIssuesResponse)
    def get(
        self,
        _request,
        build_id: str,
    ) -> Response:
        records = self.get_build_issues(build_id)
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
