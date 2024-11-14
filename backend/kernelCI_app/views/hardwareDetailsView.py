from collections import defaultdict
from django.views import View
from django.db.models import F
from datetime import datetime, timezone
from django.http import HttpResponseBadRequest, JsonResponse
from kernelCI_app.cache import getQueryCache, setQueryCache
from kernelCI_app.viewCommon import create_details_build_summary, get_details_issue
from kernelCI_app.models import Tests
from kernelCI_app.utils import (
    extract_error_message,
    extract_platform,
    getErrorResponseBody,
)
from kernelCI_app.constants.general import DEFAULT_ORIGIN

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
    required_params_get = ["origin"]
    cache_key_get = "hardwareDetailsGET"

    def sanitize_records(self, records):
        processed_builds = set()
        processed_trees = set()
        builds = {"items": [], "issues": {}}

        tests = generate_test_dict()
        boots = generate_test_dict()
        trees = []

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
            if tree_key not in processed_trees:
                processed_trees.add(tree_key)
                trees.append(get_tree(r))

            if issue_id:
                currentIssue = get_details_issue(r)
                update_issues(builds["issues"], currentIssue)
                update_issues(tests_or_boots["issues"], currentIssue)

        builds["summary"] = create_details_build_summary(builds["items"])
        properties2List(builds, ["issues"])
        properties2List(tests, ["issues", "platformsFailing", "archSummary"])
        properties2List(boots, ["issues", "platformsFailing", "archSummary"])

        return (builds, tests, boots, trees)

    def get_records(self, *, hardware_id, origin, start_datetime, end_datetime):
        records = Tests.objects.values(
            "id",
            "environment_misc",
            "path",
            "comment",
            "log_url",
            "status",
            "start_time",
            "duration",
            "misc",
            "build_id",
            "environment_compatible",
        ).annotate(
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
        ).filter(
            environment_compatible__contains=[hardware_id],
            build__checkout__start_time__gte=start_datetime,
            build__checkout__start_time__lte=end_datetime,
            origin=origin
        )
        return records

    def get(self, request, hardware_id):
        try:
            start_datetime = datetime.fromtimestamp(int(request.GET.get('startTimestampInSeconds')), timezone.utc)
            end_datetime = datetime.fromtimestamp(int(request.GET.get('endTimestampInSeconds')), timezone.utc)
        except ValueError:
            return HttpResponseBadRequest(
                getErrorResponseBody("startTimestampInSeconds and endTimestampInSeconds must be a Unix Timestamp")
            )

        origin = request.GET.get("origin", DEFAULT_ORIGIN)
        params = {
            "hardware_id": hardware_id,
            "origin": origin,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
        }

        records = getQueryCache(self.cache_key_get, params)
        if not records:
            records = self.get_records(**params)
            setQueryCache(self.cache_key_get, params, records)

        builds, tests, boots, trees = self.sanitize_records(records)

        return JsonResponse(
            {"builds": builds, "tests": tests, "boots": boots, "trees": trees}, safe=False
        )
