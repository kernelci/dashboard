from typing import Dict, List, Optional
from django.http import JsonResponse
from django.db import connection
from django.views import View

from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.utils import (
    Issue,
    convert_issues_dict_to_list,
    create_issue,
)


class IssueView(View):
    fields = ["incident_id", "id", "comment", "report_url"]

    def get_dict_record(self, row) -> Dict[str, str]:
        record = {}
        for idx, field in enumerate(self.fields):
            record[field] = row[idx]
        return record

    def sanitize_rows(self, rows) -> List[Issue]:
        result = {}
        for row in rows:
            record = self.get_dict_record(row)
            currentIssue = result.get(record["id"])
            if currentIssue:
                currentIssue["incidents_info"]["incidentsCount"] += 1
            else:
                result[record["id"]] = create_issue(
                    issue_id=record["id"],
                    issue_comment=record["comment"],
                    issue_report_url=record["report_url"],
                )
        return convert_issues_dict_to_list(result)

    def get_test_issues(self, test_id: str) -> List[Issue]:
        query = """
            SELECT
                incidents.id,
                issues.id,
                issues.comment,
                issues.report_url
            FROM incidents
            JOIN issues
                ON incidents.issue_id = issues.id
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
                incidents.present,
                issues.id,
                issues.comment,
                issues.report_url
            FROM incidents
            JOIN issues
                ON incidents.issue_id = issues.id
            WHERE incidents.build_id = %s
            """
        with connection.cursor() as cursor:
            cursor.execute(query, [build_id])
            rows = cursor.fetchall()
        return self.sanitize_rows(rows)

    def get(
        self, _request, test_id: Optional[str] = None, build_id: Optional[str] = None
    ) -> JsonResponse:
        if test_id:
            return JsonResponse(self.get_test_issues(test_id), safe=False)
        if build_id:
            return JsonResponse(self.get_build_issues(build_id), safe=False)
        return create_error_response(
            error_message="A test or build ID must be provided",
        )
