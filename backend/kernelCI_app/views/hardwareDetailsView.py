from collections import defaultdict
from datetime import timedelta
from django.views import View
from django.db.models import F
from django.utils import timezone
from django.http import JsonResponse
from kernelCI_app.viewCommon import create_details_build_summary, get_details_issue
from kernelCI_app.models import Tests
from kernelCI_app.utils import (
    extract_error_message,
    extract_platform,
)
from kernelCI_app.helpers.date import parseIntervalInDaysGetParameter
from kernelCI_app.helpers.errorHandling import ExceptionWithJsonResponse


DEFAULT_DAYS_INTERVAL = 3


def properties2List(d, keys):
    for k in keys:
        v = d[k]
        if type(v) is dict:
            d[k] = list(v.values())
        elif type(v) is set:
            d[k] = list(v)


def get_arch_summary(record):
    return {
        "arch": record["build_architecture"],
        "compiler": record["build_compiler"],
        "status": defaultdict(int)
    }


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
        "tree_name": record["checkout_tree_name"],
    }


def get_tree_key(record):
    return record["checkout_tree_name"] + \
        record["checkout_git_repository_branch"] + \
        record["checkout_git_repository_url"]


def get_tree(record):
    return {
        "tree_name": record["checkout_tree_name"],
        "git_repository_branch": record["checkout_git_repository_branch"],
        "git_repository_url": record["checkout_git_repository_url"],
        "git_commit_name": record["checkout_git_commit_name"],
        "git_commit_hash": record["checkout_git_commit_hash"],
    }


def get_history(record):
    return {
        "id": record["id"],
        "status": record["status"],
        "path": record["path"],
        "duration": record["duration"],
        "startTime": record["start_time"],
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
        "archSummary": {},
        "platformsFailing": set(),
        "statusSummary": defaultdict(int),
        "failReasons": defaultdict(int),
        "configs": defaultdict(lambda: defaultdict(int)),
        "issues": {},
    }


class HardwareDetails(View):
    def sanitize_records(self, records):
        processed_builds = set()
        builds = {"items": [], "issues": {}}

        tests = generate_test_dict()
        boots = generate_test_dict()
        trees = defaultdict(lambda: defaultdict(str))

        for r in records:
            build_id = r["build_id"]
            issue_id = r["issue_id"]
            status = r["status"]

            tests_or_boots = boots if is_boot(r) else tests

            tests_or_boots["history"].append(get_history(r))
            tests_or_boots["statusSummary"][r["status"]] += 1
            tests_or_boots["configs"][r["build_config_name"]][r["status"]] += 1

            if status == "ERROR" or status == "FAIL" or status == "MISS":
                tests_or_boots["platformsFailing"].add(
                    extract_platform(r["environment_misc"])
                )
                tests_or_boots["failReasons"][extract_error_message(r["misc"])] += 1

            archKey = f'{r["build_architecture"]}{r["build_compiler"]}'
            archSummary = tests_or_boots["archSummary"].get(archKey)
            if not archSummary:
                archSummary = get_arch_summary(r)
                tests_or_boots["archSummary"][archKey] = archSummary
            archSummary["status"][status] += 1

            if build_id not in processed_builds:
                processed_builds.add(build_id)
                builds["items"].append(get_build(r))

            tree_key = get_tree_key(r)
            trees[tree_key] = get_tree(r)
            if issue_id:
                currentIssue = get_details_issue(r)
                update_issues(builds["issues"], currentIssue)
                update_issues(tests_or_boots["issues"], currentIssue)

        builds["summary"] = create_details_build_summary(builds["items"])
        properties2List(builds, ["issues"])
        properties2List(tests, ["issues", "platformsFailing", "archSummary"])
        properties2List(boots, ["issues", "platformsFailing", "archSummary"])
        trees = list(trees.values())

        return (builds, tests, boots, trees)

    def get(self, request, hardware_id):
        try:
            days_interval = parseIntervalInDaysGetParameter(
                request.GET.get("intervalInDays", DEFAULT_DAYS_INTERVAL)
            )
        except ExceptionWithJsonResponse as e:
            return e.getJsonResponse()

        start_time = timezone.now() - timedelta(days=days_interval)

        target_tests = Tests.objects.filter(
            environment_compatible__contains=[hardware_id], start_time__gte=start_time
        ).values(
            "id",
            "origin",
            "environment_comment",
            "environment_misc",
            "path",
            "comment",
            "log_url",
            "status",
            "waived",
            "start_time",
            "duration",
            "misc",
            "build_id",
            "environment_compatible",
        )

        records = target_tests.annotate(
            build_architecture=F("build__architecture"),
            build_config_name=F("build__config_name"),
            build_misc=F("build__misc"),
            build_config_url=F("build__config_url"),
            build_compiler=F("build__compiler"),
            build_valid=F("build__valid"),
            build_duration=F("build__duration"),
            build_log_url=F("build__log_url"),
            build_start_time=F("build__start_time"),
            checkout_git_repository_url=F("build__checkout__git_repository_url"),
            checkout_git_repository_branch=F("build__checkout__git_repository_branch"),
            checkout_git_commit_name=F("build__checkout__git_commit_name"),
            checkout_git_commit_hash=F("build__checkout__git_commit_hash"),
            checkout_tree_name=F("build__checkout__tree_name"),
            issue_id=F("build__incidents__issue__id"),
            issue_comment=F("build__incidents__issue__comment"),
            issue_report_url=F("build__incidents__issue__report_url"),
        )
        builds, tests, boots, trees = self.sanitize_records(records)

        return JsonResponse(
            {"builds": builds, "tests": tests, "boots": boots, "trees": trees}, safe=False
        )
