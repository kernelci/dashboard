from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from querybuilder.query import Query
from kernelCI_app.models import Builds
from kernelCI_app.utils import (
    FilterParams,
    InvalidComparisonOP,
    convert_issues_dict_to_list,
    create_issue,
    getErrorResponseBody,
)
from utils.validation import validate_required_params


class TreeDetails(View):

    def sanitize_records(self, records):
        builds = []
        processedBuilds = set()
        issuesTable = {}
        issues = []
        for r in records:
            if r["issue_id"]:
                currentIssue = issuesTable.get(r["issue_id"])
                if currentIssue is None:
                    currentIssue = create_issue(
                        issue_id=r["issue_id"],
                        issue_comment=r["issue_comment"],
                        issue_report_url=r["issue_report_url"],
                    )
                    issuesTable[r["issue_id"]] = currentIssue
                currentIssue["incidents_info"]["incidentsCount"] += 1

            if r["id"] in processedBuilds:
                continue
            processedBuilds.add(r["id"])

            builds.append(
                {
                    "id": r["id"],
                    "architecture": r["architecture"],
                    "config_name": r["config_name"],
                    "misc": r["misc"],
                    "config_url": r["config_url"],
                    "compiler": r["compiler"],
                    "valid": r["valid"],
                    "duration": r["duration"],
                    "log_url": r["log_url"],
                    "start_time": r["start_time"],
                    "git_repository_url": r["git_repository_url"],
                    "git_repository_branch": r["git_repository_branch"],
                }
            )
        summary = self.create_summary(records)
        issues = convert_issues_dict_to_list(issuesTable)
        return (
            builds,
            summary,
            issues,
        )

    def create_default_status(self):
        return {"valid": 0, "invalid": 0, "null": 0}

    def create_summary(self, builds_dict):
        status_map = {True: "valid", False: "invalid", None: "null"}

        build_summ = self.create_default_status()
        config_summ = {}
        arch_summ = {}

        for build in builds_dict:
            status_key = status_map[build["valid"]]
            build_summ[status_key] += 1

            if config := build["config_name"]:
                status = config_summ.get(config)
                if not status:
                    status = self.create_default_status()
                    config_summ[config] = status
                status[status_key] += 1

            if arch := build["architecture"]:
                status = arch_summ.setdefault(arch, self.create_default_status())
                status[status_key] += 1
                compiler = build["compiler"]
                if compiler and compiler not in status.setdefault("compilers", []):
                    status["compilers"].append(compiler)

        return {
            "builds": build_summ,
            "configs": config_summ,
            "architectures": arch_summ,
        }

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

        for f in filter_params.filters:
            field = f["field"]
            table = None
            if field in build_fields:
                table = "builds"
            elif field in checkout_fields:
                table = "checkouts"
            if table:
                op = filter_params.get_comparison_op(f, "orm")
                query.where(**{f"{table}.{field}__{op}": f["value"]})

        records = query.select()
        builds, summary, issues = self.sanitize_records(records)

        return JsonResponse(
            {"builds": builds, "summary": summary, "issues": issues}, safe=False
        )
