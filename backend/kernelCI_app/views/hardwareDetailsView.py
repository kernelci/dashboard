from typing import Dict, Set, Literal
from collections import defaultdict
import json
from typing import Dict, List, Optional, Set, Literal
from kernelCI_app.helpers.logger import log_message
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime, timezone
from django.http import HttpResponseBadRequest, JsonResponse
from kernelCI_app.cache import getQueryCache, setQueryCache
from kernelCI_app.viewCommon import create_details_build_summary
from kernelCI_app.models import Tests
from kernelCI_app.utils import (
    create_issue,
    extract_error_message,
    extract_platform,
    getErrorResponseBody,
    toIntOrDefault,
    FilterParams,
    InvalidComparisonOP
)
from kernelCI_app.constants.general import DEFAULT_ORIGIN
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict

DEFAULT_DAYS_INTERVAL = 3
SELECTED_HEAD_TREE_VALUE = 'head'
STATUS_FAILED_VALUE = "FAIL"
NULL_STRINGS = ["null", "Unknown"]


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
        "failedWithUnknownIssues": 0,
    }


def is_record_tree_selected(record, tree, is_all_selected: bool):
    if is_all_selected:
        return True
    return tree.get("is_tree_selected") and \
        tree["git_commit_hash"] == record["build__checkout__git_commit_hash"]


def update_issues(record, task, is_failed_task):
    issue_id = record["build__incidents__issue__id"]
    if issue_id:
        existing_issue = task["issues"].get(issue_id)
        if existing_issue:
            existing_issue["incidents_info"]["incidentsCount"] += 1
        else:
            new_issue = get_details_issue(record)
            task[issue_id] = new_issue
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
        self.filterTestDurationMin, self.filterTestDurationMax = None, None
        self.filterBootDurationMin, self.filterBootDurationMax = None, None
        self.filterBuildDurationMin, self.filterBuildDurationMax = None, None
        self.filterBootStatus = set()
        self.filterTestStatus = set()
        self.filterTreeDetailsConfigs = set()
        self.filterTreeDetailsCompiler = set()
        self.filterArchitecture = set()
        self.filterTestPath = ""
        self.filterBootPath = ""
        self.filterValid = set()
        self.filter_handlers = {
            "boot.status": self.__handle_boot_status,
            "boot.duration": self.__handle_boot_duration,
            "test.status": self.__handle_test_status,
            "test.duration": self.__handle_test_duration,
            "duration": self.__handle_build_duration,
            "config_name": self.__handle_config_name,
            "compiler": self.__handle_compiler,
            "valid": self.__handle_valid,
            "architecture": self.__handle_architecture,
            "test.path": self.__handle_path,
            "boot.path": self.__handle_path,
        }

    def __handle_boot_status(self, current_filter):
        self.filterBootStatus.add(current_filter["value"])

    def __handle_boot_duration(self, current_filter):
        value = current_filter["value"][0]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterBootDurationMax = toIntOrDefault(value, None)
        else:
            self.filterBootDurationMin = toIntOrDefault(value, None)

    def __handle_test_status(self, current_filter):
        self.filterTestStatus.add(current_filter["value"])

    def __handle_test_duration(self, current_filter):
        value = current_filter["value"][0]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterTestDurationMax = toIntOrDefault(value, None)
        else:
            self.filterTestDurationMin = toIntOrDefault(value, None)

    def __handle_build_duration(self, current_filter):
        value = current_filter["value"][0]
        operation = current_filter["comparison_op"]
        if operation == "lte":
            self.filterBuildDurationMax = toIntOrDefault(value, None)
        else:
            self.filterBuildDurationMin = toIntOrDefault(value, None)

    def __handle_config_name(self, current_filter):
        self.filterTreeDetailsConfigs = self.filterTreeDetailsConfigs.union(current_filter["value"])

    def __handle_compiler(self, current_filter):
        self.filterTreeDetailsCompiler = self.filterTreeDetailsCompiler.union(current_filter["value"])

    def __handle_architecture(self, current_filter):
        self.filterArchitecture = self.filterArchitecture.union(current_filter["value"])

    def __handle_path(self, current_filter):
        if current_filter["field"] == "boot.path":
            self.filterBootPath = current_filter["value"][0]
        else:
            self.filterTestPath = current_filter["value"][0]

    def __handle_valid(self, current_filter):
        self.filterValid.add(current_filter["value"] == "Success")

    def __processFilters(self, body):
        try:
            filter_params = FilterParams(body, process_body=True)

            for current_filter in filter_params.filters:
                field = current_filter["field"]
                # Delegate to the appropriate handler based on the field
                if field in self.filter_handlers:
                    self.filter_handlers[field](current_filter)
        except InvalidComparisonOP as e:
            return HttpResponseBadRequest(getErrorResponseBody(str(e)))

    def is_build_filtered_in(
        self,
        build: Dict,
        processed_builds: Set[str],
    ) -> bool:
        is_build_not_processed = not build["id"] in processed_builds
        is_build_filtered_out = self.__build_filters_pass(build['valid'], build['duration'])
        return is_build_not_processed and is_build_filtered_out

    def __build_filters_pass(self, status: bool, duration: int):
        if len(self.filterValid) > 0 and (str(status).lower() not in self.filterValid):
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

        return True

    def __boots_filters_pass(self, status, duration):
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

        return True

    def __non_boots_filters_pass(self, status, duration):
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
                record['path'].startswith("boot")
                and self.filterBootPath != ""
                and (self.filterBootPath not in record['path'])
            )
            or (
                not record['path'].startswith("boot")
                and self.filterTestPath != ""
                and (self.filterTestPath not in record['path'])
            )
            or (
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
            test_filter_pass = self.__boots_filters_pass(record['status'], record['duration'])
        else:
            test_filter_pass = self.__non_boots_filters_pass(record['status'], record['duration'])

        return test_filter_pass

    def handle_test(self, record, tests):
        status = record["status"]

        tests["history"].append(get_history(record))
        tests["statusSummary"][record["status"]] += 1
        tests["configs"][record["build__config_name"]][record["status"]] += 1

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

        update_issues(record, tests, status == STATUS_FAILED_VALUE)

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

    def sanitize_records(self, records, trees: List, filters_map: Dict, is_all_selected: bool):
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

            should_process_test = not self.should_jump_test(test_filter_key, record, filters_map)

            pass_in_global_filters = self.pass_build_filter(record, filters_map['global'])
            if not record_tree_selected or not pass_in_global_filters:
                continue

            if should_process_test:
                self.handle_test(record, boots if is_record_boot else tests)

            should_process_build = self.is_build_filtered_in(build, filters_map, processed_builds)

            if should_process_build:
                builds["items"].append(build)
                update_issues(record, builds, record["build__valid"] is False)
                processed_builds.add(build_id)

        builds["summary"] = create_details_build_summary(builds["items"])
        properties2List(builds, ["issues"])
        properties2List(tests, ["issues", "platformsFailing", "archSummary"])
        properties2List(boots, ["issues", "platformsFailing", "archSummary"])

        return (builds, tests, boots, tree_status_summary)

    def get_trees(self, hardware_id, origin, limit_datetime):
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
            "build__incidents__issue__id",
            "build__incidents__issue__comment",
            "build__incidents__issue__report_url"
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
            filters_params = body.get("filter", {})
            selected_commits = body.get("selectedCommits", {})

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

        filters_map = self.get_filters(filters_params)

        builds, tests, boots, tree_status_summary = self.sanitize_records(
            records,
            trees_with_selected_commits,
            filters_map,
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
