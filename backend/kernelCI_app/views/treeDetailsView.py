from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from querybuilder.query import Query
from kernelCI_app.models import Builds
from kernelCI_app.utils import (
    FilterParams,
    InvalidComparisonOP,
    convert_issues_dict_to_list,
    getErrorResponseBody,
)
from kernelCI_app.viewCommon import create_details_build_summary, get_details_issue
from utils.validation import validate_required_params


def get_build(record):
    return {
        "id": record["id"],
        "architecture": record["architecture"],
        "config_name": record["config_name"],
        "misc": record["misc"],
        "config_url": record["config_url"],
        "compiler": record["compiler"],
        "valid": record["valid"],
        "duration": record["duration"],
        "log_url": record["log_url"],
        "start_time": record["start_time"],
        "git_repository_url": record["git_repository_url"],
        "git_repository_branch": record["git_repository_branch"],
    }


class TreeDetails(View):
    def sanitize_records(self, records):
        builds = []
        processedBuilds = set()
        issues_dict = {}

        for r in records:
            if r["issue_id"]:
                currentIssue = issues_dict.get(r["issue_id"])
                if currentIssue:
                    currentIssue["incidents_info"]["incidentsCount"] += 1
                else:
                    issues_dict[r["issue_id"]] = get_details_issue(r)

            build_id = r["id"]
            if build_id in processedBuilds:
                continue
            processedBuilds.add(build_id)
            builds.append(get_build(r))

        summary = create_details_build_summary(builds)
        issues = convert_issues_dict_to_list(issues_dict)
        return (
            builds,
            summary,
            issues,
        )

    # TODO, Remove this query builder, use Django ORM or raw SQL
    def get(self, request, commit_hash):
        git_url_param = request.GET.get("git_url")
        git_branch_param = request.GET.get("git_branch")
        origin = request.GET.get("origin")

        errorResponse = validate_required_params(
            request, ["origin", "git_url", "git_branch"]
        )
        if errorResponse:
            return errorResponse

        build_fields = [
            "id",
            "architecture",
            "config_name",
            "misc",
            "config_url",
            "compiler",
            "valid",
            "duration",
            "log_url",
            "start_time",
        ]
        checkout_fields = [
            "git_repository_url",
            "git_repository_branch",
        ]

        incident_fields = [{"incident_id": "id"}, {"incident_present": "present"}]
        issue_fields = [
            {"issue_id": "id"},
            {"issue_comment": "comment"},
            {"issue_report_url": "report_url"},
        ]

        query = (
            Query()
            .from_table(Builds, build_fields)
            .join(
                "checkouts",
                condition="checkouts.id = builds.checkout_id",
                fields=checkout_fields,
            )
            .where(git_commit_hash__eq=commit_hash)
            .where(git_repository_url__eq=git_url_param)
            .where(git_repository_branch__eq=git_branch_param)
            .where(**{"checkouts.origin__exact": origin})
            .join(
                "incidents",
                join_type="LEFT JOIN",
                condition="builds.id = incidents.build_id",
                fields=incident_fields,
            )
            .join(
                "issues",
                join_type="LEFT JOIN",
                condition="incidents.issue_id = issues.id",
                fields=issue_fields,
            )
        )

        try:
            filter_params = FilterParams(request)
        except InvalidComparisonOP as e:
            return HttpResponseBadRequest(getErrorResponseBody(str(e)))

        query = self.__get_filtered_tree_details_query(query, filter_params, build_fields, checkout_fields)

        records = query.select()
        builds, summary, issues = self.sanitize_records(records)

        return JsonResponse(
            {"builds": builds, "summary": summary, "issues": issues}, safe=False
        )
