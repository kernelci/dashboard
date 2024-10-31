from collections import defaultdict
from datetime import timedelta
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View
from django.db.models import F
from django.utils import timezone
from kernelCI_app.viewCommon import create_details_build_summary, get_details_issue
from kernelCI_app.models import Tests
from kernelCI_app.utils import (
    convert_issues_dict_to_list,
    extract_error_message,
    extract_platform,
    getErrorResponseBody,
)


DEFAULT_DAYS_INTERVAL = 7


def get_build(record):
    return {
        "id": record["build_id"],
        "architecture": record["build_architecture"],
        "config_name": record["build_config_name"],
        "misc": record["build_misc"],
        "config_url": record["build_config_url"],
        "compiler": record["build_compiler"],
        "valid": record["build_valid"],
        "duration": record["build_duration"],
        "log_url": record["build_log_url"],
        "start_time": record["build_start_time"],
        "git_repository_url": record["checkout_git_repository_url"],
        "git_repository_branch": record["checkout_git_repository_branch"],
    }


def get_history(record):
    return {
        "id": record["id"],
        "status": record["status"],
        "path": record["path"],
        "duration": record["duration"],
        "startTime": record["start_time"]
    }


def update_issues(issues, issue):
    existing_issue = issues.get(issue["id"])
    if existing_issue:
        existing_issue["incidents_info"]["incidentsCount"] += 1
    else:
        issues[issue["id"]] = issue


def is_boot(record):
    return record["path"] == "boot" or record["path"].startswith("boot.")


def generate_test_dict():
    return {
        "history": [],
        "platformsFailing": set(),
        "statusSummary": defaultdict(int),
        "failReasons": defaultdict(int),
        "configs": defaultdict(lambda: defaultdict(int)),
        "issues": {}
    }


class HardwareDetails(View):
    def sanitize_records(self, records):
        processed_builds = set()
        builds = {"items": [], "issues": {}}

        tests = generate_test_dict()
        boots = generate_test_dict()

        for r in records:
            build_id = r["build_id"]
            issue_id = r["issue_id"]
            status = r["status"]

            tests_or_boots = boots if is_boot(r) else tests

            tests_or_boots["history"].append(get_history(r))
            tests_or_boots["statusSummary"][r["status"]] += 1
            tests_or_boots["configs"][r["build_config_name"]][r["status"]] += 1

            if status == "ERROR" or status == "FAIL" or status == "MISS":
                tests_or_boots["platformsFailing"].add(extract_platform(r["environment_misc"]))
                tests_or_boots["failReasons"][extract_error_message(r["misc"])] += 1

            if build_id not in processed_builds:
                processed_builds.add(build_id)
                builds["items"].append(get_build(r))

            if issue_id:
                currentIssue = get_details_issue(r)
                update_issues(builds["issues"], currentIssue)
                update_issues(tests_or_boots["issues"], currentIssue)

        builds["summary"] = create_details_build_summary(builds["items"])
        builds["issues"] = convert_issues_dict_to_list(builds["issues"])
        tests["platformsFailing"] = list(tests["platformsFailing"])
        tests["issues"] = convert_issues_dict_to_list(tests["issues"])
        boots["platformsFailing"] = list(boots["platformsFailing"])
        boots["issues"] = convert_issues_dict_to_list(boots["issues"])

        return (
            builds,
            tests,
            boots
        )

    def get(self, request, hardware_id):
        try:
            days_interval = int(request.GET.get("daysInterval", DEFAULT_DAYS_INTERVAL))
        except ValueError:
            return HttpResponseBadRequest(getErrorResponseBody("Invalid daysInterval"))

        if days_interval < 1:
            return HttpResponseBadRequest(getErrorResponseBody("daysInterval must be a positive integer"))

        start_time = timezone.now() - timedelta(days=days_interval)

        target_tests = Tests.objects.filter(
            environment_compatible__contains=[hardware_id],
            start_time__gte=start_time
        ).values(
            'id', 'origin', 'environment_comment', 'environment_misc', 'path', 'comment',
            'log_url', 'status', 'waived', 'start_time', 'duration', 'misc',
            'build_id', 'environment_compatible'
        )

        records = target_tests.annotate(
            build_architecture=F('build__architecture'),
            build_config_name=F('build__config_name'),
            build_misc=F('build__misc'),
            build_config_url=F('build__config_url'),
            build_compiler=F('build__compiler'),
            build_valid=F('build__valid'),
            build_duration=F('build__duration'),
            build_log_url=F('build__log_url'),
            build_start_time=F('build__start_time'),
            checkout_git_repository_url=F('build__checkout__git_repository_url'),
            checkout_git_repository_branch=F('build__checkout__git_repository_branch'),
            issue_id=F('build__incidents__issue__id'),
            issue_comment=F('build__incidents__issue__comment'),
            issue_report_url=F('build__incidents__issue__report_url')
        )
        builds, tests, boots = self.sanitize_records(records)

        return JsonResponse(
            {
                'builds': builds,
                'tests': tests,
                'boots': boots
            },
            safe=False
        )
