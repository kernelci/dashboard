from typing import Dict, List, Optional
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError

from kernelCI_app.helpers.errorHandling import create_api_error_response
from kernelCI_app.utils import (
    convert_issues_dict_to_list,
    create_issue,
)
from http import HTTPStatus
from kernelCI_app.typeModels.issues import Issue, IssueDict
from kernelCI_app.typeModels.issuesView import IssuesResponse


class IssueView(APIView):
    fields = ["incident_id", "id", "version", "comment", "report_url"]

    def get_dict_record(self, row) -> Dict[str, str]:
        record = {}
        for idx, field in enumerate(self.fields):
            record[field] = row[idx]
        return record

    def sanitize_rows(self, rows) -> List[Issue]:
        result: IssueDict = {}
        for row in rows:
            record = self.get_dict_record(row)
            issue_id = record["id"]
            issue_version = record["version"]
            currentIssue = result.get((issue_id, issue_version))
            if currentIssue:
                currentIssue["incidents_info"]["incidentsCount"] += 1
            else:
                result[(issue_id, issue_version)] = create_issue(
                    issue_id=issue_id,
                    issue_version=issue_version,
                    issue_comment=record["comment"],
                    issue_report_url=record["report_url"],
                )
        return convert_issues_dict_to_list(result)

    def get_test_issues(self, test_id: str) -> List[Issue]:
        query = """
            SELECT
                incidents.id,
                issues.id,
                issues.version,
                issues.comment,
                issues.report_url
            FROM incidents
            JOIN issues
                ON incidents.issue_id = issues.id
                AND incidents.issue_version = issues.version
            WHERE incidents.test_id = %s
            """
        with connection.cursor() as cursor:
            cursor.execute(query, [test_id])
            rows = cursor.fetchall()

        return self.sanitize_rows(rows)

    def get_build_issues(self, build_id: str) -> List[Issue]:
        query = """
            SELECT
                incidents.id,
                issues.id,
                issues.version,
                issues.comment,
                issues.report_url
            FROM incidents
            JOIN issues
                ON incidents.issue_id = issues.id
                AND incidents.issue_version = issues.version
            WHERE incidents.build_id = %s
            """
        with connection.cursor() as cursor:
            cursor.execute(query, [build_id])
            rows = cursor.fetchall()
        return self.sanitize_rows(rows)

    @extend_schema(
        responses=IssuesResponse
    )
    def get(
        self, _request, test_id: Optional[str] = None, build_id: Optional[str] = None
    ) -> Response:
        if test_id:
            test_issues = self.get_test_issues(test_id)

            if len(test_issues) == 0:
                return create_api_error_response(
                    error_message="No issues were found for this test",
                    status_code=HTTPStatus.OK,
                )

            try:
                valid_test_response = IssuesResponse(test_issues)
            except ValidationError as e:
                return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

            return Response(valid_test_response.model_dump())

        if build_id:
            build_issues = self.get_build_issues(build_id)

            if len(build_issues) == 0:
                return create_api_error_response(
                    error_message="No issues were found for this build",
                    status_code=HTTPStatus.OK,
                )

            try:
                valid_build_response = IssuesResponse(build_issues)
            except ValidationError as e:
                return Response(data=e.json(), status=HTTPStatus.INTERNAL_SERVER_ERROR)

            return Response(valid_build_response.model_dump())

        return create_api_error_response(
            error_message="A test or build ID must be provided"
        )
