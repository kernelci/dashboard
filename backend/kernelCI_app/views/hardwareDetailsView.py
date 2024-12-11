from collections import defaultdict
import json
from typing import Dict, List, Optional, Set, Literal
from kernelCI_app.helpers.filters import (
    should_increment_test_issue,
    is_build_invalid,
    should_filter_test_issue,
)
from kernelCI_app.helpers.logger import log_message
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime, timezone
from django.http import HttpResponseBadRequest, JsonResponse
from kernelCI_app.cache import getQueryCache, setQueryCache
from kernelCI_app.viewCommon import create_details_build_summary
from kernelCI_app.models import Tests
from kernelCI_app.utils import (
    UNKNOWN_STRING,
    create_issue,
    extract_error_message,
    extract_platform,
    getErrorResponseBody,
    toIntOrDefault,
    FilterParams,
    NULL_STRINGS
)
from kernelCI_app.constants.general import DEFAULT_ORIGIN
from django.views.decorators.csrf import csrf_exempt

DEFAULT_DAYS_INTERVAL = 3
SELECTED_HEAD_TREE_VALUE = 'head'
STATUS_FAILED_VALUE = "FAIL"


def properties2List(d: Dict, keys: str):
    for k in keys:
        v = d[k]
        if type(v) is dict:
            d[k] = list(v.values())
        elif type(v) is set:
            d[k] = list(v)


def get_arch_summary(record: Dict):
    return {
        "arch": record["build__architecture"],
        "compiler": record["build__compiler"],
        "status": defaultdict(int)
    }


def get_build(record: Dict, tree_idx: int):
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
        "issue_id": record["build__incidents__issue__id"],
        "tree_index": tree_idx
    }


def get_tree_key(record: Dict):
    return record["build__checkout__tree_name"] + \
        record["build__checkout__git_repository_branch"] + \
        record["build__checkout__git_repository_url"]


def get_tree(record: Dict):
    return {
        "tree_name": record["build__checkout__tree_name"],
        "git_repository_branch": record["build__checkout__git_repository_branch"],
        "git_repository_url": record["build__checkout__git_repository_url"],
        "git_commit_name": record["build__checkout__git_commit_name"],
        "git_commit_hash": record["build__checkout__git_commit_hash"],
    }


def get_history(record: Dict):
    return {
        "id": record["id"],
        "status": record["status"],
        "path": record["path"],
        "duration": record["duration"],
        "startTime": record["start_time"],
    }


def is_boot(record: Dict) -> bool:
    return record["path"] == "boot" or record["path"].startswith("boot.")


def get_record_tree(record: Dict, selected_trees: List) -> Optional[Dict]:
    for tree in selected_trees:
        if (
            tree["tree_name"] == record["build__checkout__tree_name"]
            and tree["git_repository_branch"] == record["build__checkout__git_repository_branch"]
            and tree["git_repository_url"] == record["build__checkout__git_repository_url"]
        ):
            return tree

    return None


def generate_test_dict():
    return {
        "history": [],
        "archSummary": {},
        "platformsFailing": set(),
        "statusSummary": defaultdict(int),
        "failReasons": defaultdict(int),
        "configs": defaultdict(lambda: defaultdict(int)),
        "issues": {},
        "failedWithUnknownIssues": 0,
    }


def is_record_tree_selected(record, tree, is_all_selected: bool):
    if is_all_selected:
        return True
    return tree.get("is_tree_selected") and \
        tree["git_commit_hash"] == record["build__checkout__git_commit_hash"]


# TODO unify with treeDetails
def update_issues(
    issue_id: Optional[str],
    incident_test_id: Optional[str],
    build_valid: Optional[bool],
    issue_comment: Optional[str],
    issue_report_url: Optional[str],
    task,
    is_failed_task: bool,
    issue_from: str,
) -> None:
    can_insert_issue = True
    if (issue_from == "build"):
        can_insert_issue = is_build_invalid(build_valid)
    elif (issue_from == "test"):
        can_insert_issue = should_increment_test_issue(issue_id, incident_test_id)

    if issue_id and can_insert_issue:
        existing_issue = task["issues"].get(issue_id)
        if existing_issue:
            existing_issue["incidents_info"]["incidentsCount"] += 1
        else:
            new_issue = create_issue(
                issue_id=issue_id,
                issue_comment=issue_comment,
                issue_report_url=issue_report_url,
            )
            task["issues"][issue_id] = new_issue
    elif is_failed_task:
        task["failedWithUnknownIssues"] += 1


def generate_tree_status_summary_dict():
    return {
        "builds": defaultdict(int),
        "boots": defaultdict(int),
        "tests": defaultdict(int)
    }


def get_build_status(is_build_valid):
    if is_build_valid is True:
        return "valid"
    elif is_build_valid is False:
        return "invalid"

    # can be None
    return "null"


# disable django csrf protection https://docs.djangoproject.com/en/5.0/ref/csrf/
# that protection is recommended for ‘unsafe’ methods (POST, PUT, and DELETE)
# but we are using POST here just to follow the convention to use the request body
# also the csrf protection require the usage of cookies which is not currently
# supported in this project
@method_decorator(csrf_exempt, name='dispatch')
class HardwareDetails(View):
    required_params_get = ["origin"]
    cache_key_get_tree_data = "hardwareDetailsTreeData"
    cache_key_get_full_data = "hardwareDetailsFullData"

    def __init__(self):
        self.filterParams = None

    def setup_filters(self):
        self.filterTestDurationMin = self.filterParams.filterTestDurationMin
        self.filterTestDurationMax = self.filterParams.filterTestDurationMax
        self.filterBootDurationMin = self.filterParams.filterBootDurationMin
        self.filterBootDurationMax = self.filterParams.filterBootDurationMax
        self.filterBuildDurationMin = self.filterParams.filterBuildDurationMin
        self.filterBuildDurationMax = self.filterParams.filterBuildDurationMax
        self.filterBootStatus = self.filterParams.filterBootStatus
        self.filterTestStatus = self.filterParams.filterTestStatus
        self.filterTreeDetailsConfigs = self.filterParams.filterConfigs
        self.filterTreeDetailsCompiler = self.filterParams.filterCompiler
        self.filterArchitecture = self.filterParams.filterArchitecture
        self.filterTestPath = self.filterParams.filterTestPath
        self.filterBootPath = self.filterParams.filterBootPath
        self.filterValid = self.filterParams.filterBuildValid
        self.filterIssues = self.filterParams.filterIssues

    def is_build_filtered_in(
        self,
        build: Dict,
        processed_builds: Set[str],
    ) -> bool:
        is_build_not_processed = not build["id"] in processed_builds
        is_build_filtered_out = self._build_filters_pass(
            valid=build["valid"],
            duration=build["duration"],
            issue_id=build["issue_id"]
        )
        return is_build_not_processed and is_build_filtered_out

    def _build_filters_pass(
        self, valid: Optional[bool], duration: Optional[int], issue_id: Optional[str]
    ) -> bool:
        if len(self.filterValid) > 0 and (str(valid).lower() not in self.filterValid):
            return False
        if (
            self.filterBuildDurationMax is not None or self.filterBuildDurationMin is not None
        ) and duration is None:
            return False
        if self.filterBuildDurationMax is not None and (
            toIntOrDefault(duration, 0) > self.filterBuildDurationMax
        ):
            return False
        if self.filterBuildDurationMin is not None and (
            toIntOrDefault(duration, 0) < self.filterBuildDurationMin
        ):
            return False
        if (
            len(self.filterIssues["build"]) > 0
            and (
                issue_id not in self.filterIssues["build"]
                or valid is True
            )
        ):
            return False

        return True

    def _boots_filters_pass(
        self,
        status: Optional[str],
        duration: Optional[int],
        path: Optional[str],
        issue_id: Optional[str],
        incidents_test_id: Optional[str],
    ) -> bool:
        if (
            self.filterBootPath != ""
            and (self.filterBootPath not in path)
        ):
            return False
        if len(self.filterBootStatus) > 0 and (status not in self.filterBootStatus):
            return False
        if (
            self.filterBootDurationMax is not None or self.filterBootDurationMin is not None
        ) and duration is None:
            return False
        if self.filterBootDurationMax is not None and (
            toIntOrDefault(duration, 0) > self.filterBootDurationMax
        ):
            return False
        if self.filterBootDurationMin is not None and (
            toIntOrDefault(duration, 0) < self.filterBootDurationMin
        ):
            return False
        if should_filter_test_issue(
            self.filterIssues["boot"],
            issue_id,
            incidents_test_id,
        ):
            return False

        return True

    def _non_boots_filters_pass(
        self,
        status: Optional[str],
        duration: Optional[int],
        path: Optional[str],
        issue_id: Optional[str],
        incidents_test_id: Optional[str],
    ) -> bool:
        if (
            self.filterTestPath != ""
            and (self.filterTestPath not in path)
        ):
            return False
        if len(self.filterTestStatus) > 0 and (status not in self.filterTestStatus):
            return False
        if (
            self.filterTestDurationMax is not None or self.filterTestDurationMin is not None
        ) and duration is None:
            return False
        if self.filterTestDurationMax is not None and (
            toIntOrDefault(duration, 0) > self.filterTestDurationMax
        ):
            return False
        if self.filterTestDurationMin is not None and (
            toIntOrDefault(duration, 0) < self.filterTestDurationMin
        ):
            return False
        if should_filter_test_issue(
            self.filterIssues["test"],
            issue_id,
            incidents_test_id,
        ):
            return False

        return True

    def record_in_filter(
        self,
        record: Dict,
    ) -> bool:
        record_arch_null_accept = (
            not record['build__architecture']
            and any(null_string in self.filterArchitecture for null_string in NULL_STRINGS)
        )
        record_compiler_null_accept = (
            not record['build__compiler']
            and any(null_string in self.filterTreeDetailsCompiler for null_string in NULL_STRINGS)
        )
        record_config_null_accept = (
            not record['build__config_name']
            and any(null_string in self.filterTreeDetailsConfigs for null_string in NULL_STRINGS)
        )

        if (
            (
                len(self.filterArchitecture) > 0
                and (
                    record['build__architecture'] not in self.filterArchitecture
                    and not record_arch_null_accept
                )
            )
            or (
                len(self.filterTreeDetailsCompiler) > 0
                and (
                    record['build__compiler'] not in self.filterTreeDetailsCompiler
                    and not record_compiler_null_accept
                )
            )
            or (
                len(self.filterTreeDetailsConfigs) > 0
                and (
                    record['build__config_name'] not in self.filterTreeDetailsConfigs
                    and not record_config_null_accept
                )
            )
        ):
            return False

        return True

    def test_in_filter(
        self,
        table_test: Literal["boot", "test"],
        record: Dict
    ) -> bool:
        test_filter_pass = True
        if table_test == "boot":
            test_filter_pass = self._boots_filters_pass(
                status=record["status"],
                duration=record["duration"],
                path=record["path"],
                issue_id=record["incidents__issue__id"],
                incidents_test_id=record["incidents__test_id"]
            )
        else:
            test_filter_pass = self._non_boots_filters_pass(
                status=record["status"],
                duration=record["duration"],
                path=record["path"],
                issue_id=record["incidents__issue__id"],
                incidents_test_id=record["incidents__test_id"]
            )

        return test_filter_pass

    def handle_test(self, record, tests):
        status = record["status"]

        tests["history"].append(get_history(record))
        tests["statusSummary"][status] += 1
        tests["configs"][record["build__config_name"]][status] += 1

        if status == "ERROR" or status == "FAIL" or status == "MISS":
            tests["platformsFailing"].add(
                extract_platform(record["environment_misc"])
            )
            tests["failReasons"][extract_error_message(record["misc"])] += 1

        archKey = f'{record["build__architecture"]}{record["build__compiler"]}'
        archSummary = tests["archSummary"].get(archKey)
        if not archSummary:
            archSummary = get_arch_summary(record)
            tests["archSummary"][archKey] = archSummary
        archSummary["status"][status] += 1

        update_issues(
            issue_id=record["incidents__issue__id"],
            incident_test_id=record["incidents__test_id"],
            build_valid=record["build__valid"],
            issue_comment=record["incidents__issue__comment"],
            issue_report_url=record["incidents__issue__report_url"],
            task=tests,
            is_failed_task=status == STATUS_FAILED_VALUE,
            issue_from="test"
        )

    def get_filter_options(self, records, selected_trees, is_all_selected: bool):
        configs = set()
        archs = set()
        compilers = set()

        for r in records:
            current_tree = get_record_tree(r, selected_trees)
            if not current_tree or not is_record_tree_selected(r, current_tree, is_all_selected):
                continue

            configs.add(r['build__config_name'])
            archs.add(r['build__architecture'])
            compilers.add(r['build__compiler'])

        return list(configs), list(archs), list(compilers)

    # Status Summary should be unaffected by filters because it is placed above filters in the UI
    def handle_tree_status_summary(
        self,
        record: Dict,
        tree_status_summary: Dict,
        tree_index: str,
        processed_builds: Set[str],
        is_record_boot: bool,
    ) -> None:
        tree_status_key = "boots" if is_record_boot else "tests"
        tree_status_summary[tree_index][tree_status_key][record["status"]] += 1

        if record["build_id"] not in processed_builds:
            build_status = get_build_status(record["build__valid"])
            tree_status_summary[tree_index]["builds"][build_status] += 1

    def sanitize_records(self, records, trees: List, is_all_selected: bool):
        processed_builds = set()
        tests = generate_test_dict()
        boots = generate_test_dict()
        tree_status_summary = defaultdict(generate_tree_status_summary_dict)
        builds = {"items": [], "issues": {}, "failedWithUnknownIssues": 0}

        for record in records:
            current_tree = get_record_tree(record, trees)
            if not current_tree:
                log_message(f"Tree not found for record: {record}")
                continue

            self._assign_default_record_values(record)

            tree_index = current_tree["index"]
            is_record_boot = is_boot(record)
            # TODO -> Unify with tree_status_key, be careful with the pluralization
            test_filter_key = "boot" if is_record_boot else "test"

            build_id = record["build_id"]
            build = get_build(record, tree_index)

            record_tree_selected = is_record_tree_selected(record, current_tree, is_all_selected)

            self.handle_tree_status_summary(
                record,
                tree_status_summary,
                tree_index,
                processed_builds,
                is_record_boot,
            )

            pass_in_global_filters = self.record_in_filter(record)
            if not record_tree_selected or not pass_in_global_filters:
                processed_builds.add(build_id)
                continue

            should_process_test = self.test_in_filter(test_filter_key, record)

            if should_process_test:
                self.handle_test(record, boots if is_record_boot else tests)

            should_process_build = self.is_build_filtered_in(build, processed_builds)

            processed_builds.add(build_id)
            if should_process_build:
                builds["items"].append(build)
                update_issues(
                    issue_id=record["incidents__issue__id"],
                    incident_test_id=record["incidents__test_id"],
                    build_valid=record["build__valid"],
                    issue_comment=record["incidents__issue__comment"],
                    issue_report_url=record["incidents__issue__report_url"],
                    task=builds,
                    is_failed_task=record["build__valid"] is not True,
                    issue_from="build"
                )

        builds["summary"] = create_details_build_summary(builds["items"])
        properties2List(builds, ["issues"])
        properties2List(tests, ["issues", "platformsFailing", "archSummary"])
        properties2List(boots, ["issues", "platformsFailing", "archSummary"])

        return (builds, tests, boots, tree_status_summary)

    def _assign_default_record_values(self, record: Dict) -> None:
        if (record["build__architecture"] is None):
            record["build__architecture"] = UNKNOWN_STRING
        if (record["build__compiler"] is None):
            record["build__compiler"] = UNKNOWN_STRING
        if (record["build__config_name"] is None):
            record["build__config_name"] = UNKNOWN_STRING
        if (record["build__incidents__issue__id"] is None and record["build__valid"] is not True):
            record["build__incidents__issue__id"] = UNKNOWN_STRING
        if (record["incidents__issue__id"] is None and record["status"] == STATUS_FAILED_VALUE):
            record["incidents__issue__id"] = UNKNOWN_STRING

    def get_trees(self, hardware_id: str, origin: str, limit_datetime: int):
        tree_id_fields = [
            "build__checkout__tree_name",
            "build__checkout__git_repository_branch",
            "build__checkout__git_repository_url",
        ]

        trees_query_set = Tests.objects.filter(
            environment_compatible__contains=[hardware_id],
            origin=origin,
            build__checkout__start_time__lte=limit_datetime,
        ).values(
            *tree_id_fields,
            "build__checkout__git_commit_name",
            "build__checkout__git_commit_hash",
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
                "index": str(idx),
            })

        return trees

    def get_displayed_commit(self, tree: Dict, selected_commit: Optional[str]):
        if (not selected_commit) or (selected_commit == SELECTED_HEAD_TREE_VALUE):
            return tree["headGitCommitHash"]
        return selected_commit

    def get_trees_with_selected_commit(self, trees: List, selected_commits: Dict):
        selected = []

        for tree in trees:
            tree_idx = tree["index"]

            raw_selected_commit = selected_commits.get(tree_idx)

            is_tree_selected = raw_selected_commit is not None

            displayed_commit = self.get_displayed_commit(tree, raw_selected_commit)

            selected.append({
                "tree_name": tree["treeName"],
                "git_repository_branch": tree["gitRepositoryBranch"],
                "git_repository_url": tree["gitRepositoryUrl"],
                "index": tree["index"],
                "git_commit_hash": displayed_commit,
                "is_tree_selected": is_tree_selected
            })

        return selected

    def get_full_tests(self, *, hardware_id, origin, trees):
        commit_hashes = [tree["git_commit_hash"] for tree in trees]

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
            "build__checkout__tree_name",
            "incidents__id",
            "incidents__issue__id",
            "incidents__issue__comment",
            "incidents__issue__report_url",
            "incidents__test_id",
            "build__incidents__issue__id"
        ).filter(
            origin=origin,
            environment_compatible__contains=[hardware_id],
            # TODO Treat commit_hash collision (it can happen between repos)
            build__checkout__git_commit_hash__in=commit_hashes,
        )
        return records

    # Using post to receive a body request
    def post(self, request, hardware_id):
        try:
            body = json.loads(request.body)

            origin = body.get("origin", DEFAULT_ORIGIN)
            limit_datetime = datetime.fromtimestamp(
                int(body.get('limitTimestampInSeconds')),
                timezone.utc
            )

            selected_commits = body.get("selectedCommits", {})
            self.filterParams = FilterParams(body, process_body=True)
            self.setup_filters()

            is_all_selected = len(selected_commits) == 0
        except json.JSONDecodeError:
            return HttpResponseBadRequest(
                getErrorResponseBody(
                    "Invalid body, request body must be a valid json string"
                )
            )
        except (ValueError, TypeError):
            return HttpResponseBadRequest(
                getErrorResponseBody("limitTimestampInSeconds must be a Unix Timestamp")
            )

        cache_params = {
            "hardware_id": hardware_id,
            "origin": origin,
            "selected_commits": json.dumps(selected_commits),
            "limit_datetime": limit_datetime
        }

        trees = getQueryCache(self.cache_key_get_tree_data, cache_params)

        if not trees:
            trees = self.get_trees(hardware_id, origin, limit_datetime)
            setQueryCache(self.cache_key_get_tree_data, cache_params, trees)

        trees_with_selected_commits = self.get_trees_with_selected_commit(
            trees,
            selected_commits
        )

        params = {
            "hardware_id": hardware_id,
            "origin": origin,
            "trees": trees_with_selected_commits
        }

        records = getQueryCache(self.cache_key_get_full_data, cache_params)

        if not records:
            records = self.get_full_tests(**params)
            setQueryCache(self.cache_key_get_full_data, params, records)

        builds, tests, boots, tree_status_summary = self.sanitize_records(
            records,
            trees_with_selected_commits,
            is_all_selected
        )

        configs, archs, compilers = self.get_filter_options(
            records, trees_with_selected_commits, is_all_selected
        )

        trees_with_status_count = []
        for tree in trees:
            summary = tree_status_summary.get(tree["index"])
            trees_with_status_count.append({**tree, "selectedCommitStatusSummary": summary})

        return JsonResponse(
            {
                "builds": builds,
                "tests": tests,
                "boots": boots,
                "configs": configs,
                "archs": archs,
                "compilers": compilers,
                "trees": trees_with_status_count,
            }, safe=False
        )
