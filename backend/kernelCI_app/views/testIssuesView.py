from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError

from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.helpers.detailsIssues import sanitize_details_issues_rows
from kernelCI_app.helpers.errorHandling import create_api_error_response
from http import HTTPStatus
from kernelCI_app.typeModels.issues import Issue
from kernelCI_app.typeModels.detailsIssuesView import DetailsIssuesResponse


class TestIssuesView(APIView):
    def get_test_issues(self, test_id: str) -> list[Issue]:
        query = """
            SELECT
                incidents.id,
                issues.id,
                issues.version,
                issues.comment,
                issues.report_url,
                tests.status AS status
            FROM incidents
            JOIN issues
                ON incidents.issue_id = issues.id
                AND incidents.issue_version = issues.version
            JOIN tests
                ON incidents.test_id = tests.id
            WHERE incidents.test_id = %s
            """
        with connection.cursor() as cursor:
            cursor.execute(query, [test_id])
            rows = dict_fetchall(cursor=cursor)

        return rows

    @extend_schema(responses=DetailsIssuesResponse)
    def get(
        self,
        _request,
        test_id: str,
    ) -> Response:
        records = self.get_test_issues(test_id)
        test_issues = sanitize_details_issues_rows(rows=records)

        if len(test_issues) == 0:
            return create_api_error_response(
                error_message="No issues were found for this test",
                status_code=HTTPStatus.OK,
            )

        try:
            valid_test_response = DetailsIssuesResponse(test_issues)
        except ValidationError as e:
            return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return Response(valid_test_response.model_dump())
