from collections import defaultdict
import json
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime, timezone
from django.http import HttpResponseBadRequest, JsonResponse
from kernelCI_app.cache import getQueryCache, setQueryCache
from kernelCI_app.viewCommon import create_default_build_status, create_details_build_summary
from kernelCI_app.models import Tests
from kernelCI_app.utils import (
    create_issue,
    extract_error_message,
    extract_platform,
    getErrorResponseBody,
)
from kernelCI_app.constants.general import DEFAULT_ORIGIN
from django.views.decorators.csrf import csrf_exempt

DEFAULT_DAYS_INTERVAL = 3
SELECTED_VALUE = 'selected'

build_status_map = {True: "valid", False: "invalid", None: "null"}

def properties2List(d, keys):
    for k in keys:
        v = d[k]
        if type(v) is dict:
            d[k] = list(v.values())
        elif type(v) is set:
            d[k] = list(v)


def get_arch_summary(record):
    return {
        "arch": record["build__architecture"],
        "compiler": record["build__compiler"],
        "status": defaultdict(int)
    }


def get_build(record, tree_idx):
    return {
        "id": record["build_id"],
        "architecture": record["build__architecture"],
        "config_name": record["build__config_name"],
        "misc": record["build__misc"],
        "config_url": record["build__config_url"],
        "compiler": record["build__compiler"],
        "valid": record["build__valid"],
        "duration": record["build__duration"],
        "log_url": record["build__log_url"],
        "start_time": record["build__start_time"],
        "git_repository_url": record["build__checkout__git_repository_url"],
        "git_repository_branch": record["build__checkout__git_repository_branch"],
        "tree_name": record["build__checkout__tree_name"],
        "tree_index": tree_idx
    }


def get_tree_key(record):
    return record["build__checkout__tree_name"] + \
        record["build__checkout__git_repository_branch"] + \
        record["build__checkout__git_repository_url"]


def get_tree(record):
    return {
        "tree_name": record["build__checkout__tree_name"],
        "git_repository_branch": record["build__checkout__git_repository_branch"],
        "git_repository_url": record["build__checkout__git_repository_url"],
        "git_commit_name": record["build__checkout__git_commit_name"],
        "git_commit_hash": record["build__checkout__git_commit_hash"],
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


def get_current_selected_tree(record, selected_trees):
    for tree in selected_trees:
        if (
            tree["treeName"] == record["build__checkout__tree_name"]
            and tree["gitRepositoryBranch"] == record["build__checkout__git_repository_branch"]
            and tree["gitRepositoryUrl"] == record["build__checkout__git_repository_url"]
        ):
            return tree

    return None


def get_details_issue(record):
    return create_issue(
        issue_id=record["build__incidents__issue__id"],
        issue_comment=record["build__incidents__issue__comment"],
        issue_report_url=record["build__incidents__issue__report_url"],
    )


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

def generate_commit_summary():
    return {
        "earliestStartTime": "1970-01-01T00:00:00", #epoch in iso8601
        "buildStatus": create_default_build_status(),
        "bootStatus": defaultdict(int),
        "testStatus": defaultdict(int),
    }

def handle_commit_summary(commit_summary, record):
    status_key = 'bootStatus' if is_boot(record) else 'testStatus'
    commit_summary[status_key][record["status"]] += 1
    build_status = build_status_map[record["build__valid"]]
    commit_summary["buildStatus"][build_status] += 1

    print('tttype:', type(record["build__checkout__start_time"]))
    print('iso8601:', record["build__checkout__start_time"].isoformat())
    # if record["build__checkout__start_time"] > commit_summary["earliestStartTime"]:
    #    commit_summary["earliestStartTime"] = record["build__checkout__start_time"]



def is_record_in_tree_head(record, tree):
    return record["build__checkout__git_commit_hash"] == tree["headGitCommitHash"]

# def get_commit():
#     {
#         "git_commit_hash": row[0],
#         "git_commit_name": row[1],
#         "earliest_start_time": row[2],
#         "builds": {
#             "valid_builds": row[3] or 0,
#             "invalid_builds": row[4] or 0,
#             "null_builds": row[5] or 0,
#         },
#         "boots_tests": {
#             "fail_count": row[6] or 0,
#             "error_count": row[7] or 0,
#             "miss_count": row[8] or 0,
#             "pass_count": row[9] or 0,
#             "done_count": row[10] or 0,
#             "skip_count": row[11] or 0,
#             "null_count": row[12] or 0,
#         },
#         "non_boots_tests": {
#             "fail_count": row[13] or 0,
#             "error_count": row[14] or 0,
#             "miss_count": row[15] or 0,
#             "pass_count": row[16] or 0,
#             "done_count": row[17] or 0,
#             "skip_count": row[18] or 0,
#             "null_count": row[19] or 0,
#         },
#     }


# disable django csrf protection https://docs.djangoproject.com/en/5.0/ref/csrf/
# that protection is recommended for ‘unsafe’ methods (POST, PUT, and DELETE)
# but we are using POST here just to follow the convention to use the request body
# also the csrf protection require the usage of cookies which is not currently
# supported in this project
@method_decorator(csrf_exempt, name='dispatch')
class HardwareDetails(View):
    required_params_get = ["origin"]
    cache_key_get = "hardwareDetailsGET"

    def sanitize_records(self, records, selected_trees):
        processed_builds = set()
        processed_commits = set()
        builds = {"items": [], "issues": {}}

        tests = generate_test_dict()
        boots = generate_test_dict()
        commit_history = defaultdict(list)
        commit_summaries = {}


        for r in records:
            commit_hash = r["build__checkout__git_commit_hash"]
            current_tree = get_current_selected_tree(r, selected_trees)

            if not current_tree:
                continue

            tree_index = current_tree["index"]

            if commit_hash not in processed_commits:
                processed_commits.add(commit_hash)
                commit_history[tree_index].append({
                    "git_commit_hash": r["build__checkout__git_commit_hash"],
                    "git_commit_name": r["build__checkout__git_commit_name"],
                })
                commit_summaries[commit_hash] = generate_commit_summary()

            handle_commit_summary(commit_summaries[commit_hash], r)


            if not is_record_in_tree_head(r, current_tree):
                continue

            build_id = r["build_id"]
            issue_id = r["build__incidents__issue__id"]
            status = r["status"]
            tests_or_boots = boots if is_boot(r) else tests

            tests_or_boots["history"].append(get_history(r))
            tests_or_boots["statusSummary"][r["status"]] += 1
            tests_or_boots["configs"][r["build__config_name"]][r["status"]] += 1

            if status == "ERROR" or status == "FAIL" or status == "MISS":
                tests_or_boots["platformsFailing"].add(
                    extract_platform(r["environment_misc"])
                )
                tests_or_boots["failReasons"][extract_error_message(r["misc"])] += 1

            archKey = f'{r["build__architecture"]}{r["build__compiler"]}'
            archSummary = tests_or_boots["archSummary"].get(archKey)
            if not archSummary:
                archSummary = get_arch_summary(r)
                tests_or_boots["archSummary"][archKey] = archSummary
            archSummary["status"][status] += 1

            if build_id not in processed_builds:
                processed_builds.add(build_id)
                builds["items"].append(get_build(r, current_tree["index"]))

            if issue_id:
                currentIssue = get_details_issue(r)
                update_issues(builds["issues"], currentIssue)
                update_issues(tests_or_boots["issues"], currentIssue)

        for k, v in commit_history.items():
           print('commit:', k, v)

        print(records[0]["build__checkout__start_time"])
        builds["summary"] = create_details_build_summary(builds["items"])
        properties2List(builds, ["issues"])
        properties2List(tests, ["issues", "platformsFailing", "archSummary"])
        properties2List(boots, ["issues", "platformsFailing", "archSummary"])

        return (builds, tests, boots, commit_summaries)

    def get_trees(self, hardware_id, origin, start_datetime, end_datetime):
        tree_id_fields = [
            "build__checkout__tree_name",
            "build__checkout__git_repository_branch",
            "build__checkout__git_repository_url",
        ]

        trees_query_set = Tests.objects.filter(
            environment_compatible__contains=[hardware_id],
            origin=origin,
            build__checkout__start_time__gte=start_datetime,
            build__checkout__start_time__lte=end_datetime,
        ).values(
            *tree_id_fields,
            "build__checkout__git_commit_name",
            "build__checkout__git_commit_hash",
            "build__checkout__start_time"
        ).distinct(
            *tree_id_fields,
        ).order_by(
            *tree_id_fields,
            "-build__checkout__start_time"
        )

        trees = []
        for idx, tree in enumerate(trees_query_set):
            trees.append({
                "treeName": tree["build__checkout__tree_name"],
                "gitRepositoryBranch": tree["build__checkout__git_repository_branch"],
                "gitRepositoryUrl": tree["build__checkout__git_repository_url"],
                "headGitCommitName": tree["build__checkout__git_commit_name"],
                "headGitCommitHash": tree["build__checkout__git_commit_hash"],
                "earliestCheckoutStartTime": tree["build__checkout__start_time"],
                "index": str(idx),
            })

        return trees

    def get_selected_trees(self, trees, selected_trees):
        def filter_fn(tree):
            return selected_trees.get(tree.get('index')) == SELECTED_VALUE

        return list(filter(filter_fn, trees)) if selected_trees else trees

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
            "build__architecture",
            "build__config_name",
            "build__misc",
            "build__config_url",
            "build__compiler",
            "build__valid",
            "build__duration",
            "build__log_url",
            "build__start_time",
            "build__checkout__git_repository_url",
            "build__checkout__git_repository_branch",
            "build__checkout__git_commit_name",
            "build__checkout__git_commit_hash",
            "build__checkout__start_time",
            "build__checkout__tree_name",
            "build__incidents__issue__id",
            "build__incidents__issue__comment",
            "build__incidents__issue__report_url"
        ).filter(
            environment_compatible__contains=[hardware_id],
            build__checkout__start_time__gte=start_datetime,
            build__checkout__start_time__lte=end_datetime,
            origin=origin
        )
        return records

    # Using post to receive a body request
    def post(self, request, hardware_id):

        try:
            body = json.loads(request.body)
            origin = body.get("origin", DEFAULT_ORIGIN)
            start_datetime = datetime.fromtimestamp(
                int(body.get('startTimestampInSeconds')),
                timezone.utc
            )
            end_datetime = datetime.fromtimestamp(
                int(body.get('endTimestampInSeconds')),
                timezone.utc
            )
        except json.JSONDecodeError:
            return HttpResponseBadRequest(
                getErrorResponseBody(
                    "Invalid body, request body must be a valid json string"
                )
            )
        except (ValueError, TypeError):
            return HttpResponseBadRequest(
                getErrorResponseBody(
                    "startTimestampInSeconds and endTimestampInSeconds must be a Unix Timestamp"
                )
            )

        trees = self.get_trees(hardware_id, origin, start_datetime, end_datetime)
        selected_trees = self.get_selected_trees(trees, body.get('selectedTrees', {}))

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

        builds, tests, boots, commit_summaries = self.sanitize_records(records, selected_trees)

        return JsonResponse(
            {"builds": builds, "tests": tests, "boots": boots, "trees": trees, "commit_summaries": commit_summaries}, safe=False
        )
