from collections import defaultdict
from django.db.models import Subquery
from http import HTTPStatus
import json
from typing import Dict, List, Optional, Set, Literal
from kernelCI_app.helpers.filters import (
    should_increment_build_issue,
    should_increment_test_issue,
)
from kernelCI_app.helpers.errorHandling import create_error_response
from kernelCI_app.helpers.logger import log_message
from django.utils.decorators import method_decorator
from django.views import View
from datetime import datetime, timezone
from django.http import JsonResponse
from kernelCI_app.cache import getQueryCache, setQueryCache
from kernelCI_app.viewCommon import create_details_build_summary
from kernelCI_app.models import Tests
from kernelCI_app.utils import (
    create_issue,
    extract_error_message,
    is_boot
)
from django.views.decorators.csrf import csrf_exempt
from kernelCI_app.helpers.trees import get_tree_heads
from kernelCI_app.helpers.filters import UNKNOWN_STRING, FilterParams
from kernelCI_app.helpers.misc import (
    handle_environment_misc,
    env_misc_value_or_default,
)
from kernelCI_app.typeModels.hardwareDetails import PostBody, DefaultRecordValues
from pydantic import ValidationError

DEFAULT_DAYS_INTERVAL = 3
SELECTED_HEAD_TREE_VALUE = "head"
STATUS_FAILED_VALUE = "FAIL"

BuildStatusType = Literal["valid", "invalid", "null"]


def mutate_properties_to_list(dict: Dict, keys: List[str]) -> None:
    for key in keys:
        value = dict[key]
        if isinstance(value, Dict):
            dict[key] = list(value.values())
        elif isinstance(value, Set):
            dict[key] = list(value)


def get_arch_summary(record: Dict):
    return {
        "arch": record["build__architecture"],
        "compiler": record["build__compiler"],
        "status": defaultdict(int),
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
        "issue_version": record["build__incidents__issue__version"],
        "tree_index": tree_idx,
    }


def get_tree_key(record: Dict):
    return (
        record["build__checkout__tree_name"]
        + record["build__checkout__git_repository_branch"]
        + record["build__checkout__git_repository_url"]
    )


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


def get_record_tree(record: Dict, selected_trees: List) -> Optional[Dict]:
    for tree in selected_trees:
        if (
            tree["tree_name"] == record["build__checkout__tree_name"]
            and tree["git_repository_branch"]
            == record["build__checkout__git_repository_branch"]
            and tree["git_repository_url"]
            == record["build__checkout__git_repository_url"]
        ):
            return tree

    return None


def generate_test_dict():
    return {
        "history": [],
        "archSummary": {},
        "platforms": defaultdict(lambda: defaultdict(int)),
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
    return (
        tree.get("is_tree_selected")
        and tree["git_commit_hash"] == record["build__checkout__git_commit_hash"]
    )


# TODO unify with treeDetails
def update_issues(
    issue_id: Optional[str],
    issue_version: Optional[str],
    incident_test_id: Optional[str],
    build_valid: Optional[bool],
    issue_comment: Optional[str],
    issue_report_url: Optional[str],
    task,
    is_failed_task: bool,
    issue_from: str,
) -> None:
    can_insert_issue = True
    if issue_from == "build":
        (issue_id, can_insert_issue) = should_increment_build_issue(
            issue_id=issue_id,
            incident_test_id=incident_test_id,
            build_valid=build_valid,
        )
    elif issue_from == "test":
        (issue_id, can_insert_issue) = should_increment_test_issue(issue_id, incident_test_id)

    if issue_id and issue_version is not None and can_insert_issue:
        existing_issue = task["issues"].get((issue_id, issue_version))
        if existing_issue:
            existing_issue["incidents_info"]["incidentsCount"] += 1
        else:
            new_issue = create_issue(
                issue_id=issue_id,
                issue_version=issue_version,
                issue_comment=issue_comment,
                issue_report_url=issue_report_url,
            )
            task["issues"][(issue_id, issue_version)] = new_issue
    elif is_failed_task:
        task["failedWithUnknownIssues"] += 1


def generate_tree_status_summary_dict():
    return {
        "builds": defaultdict(int),
        "boots": defaultdict(int),
        "tests": defaultdict(int),
    }


def get_build_status(is_build_valid) -> BuildStatusType:
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
@method_decorator(csrf_exempt, name="dispatch")
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

    def build_in_filter(
        self,
        build: Dict,
        processed_builds: Set[str],
        incident_test_id: Optional[str],
    ) -> bool:
        is_build_not_processed = build["id"] not in processed_builds
        is_build_filtered_out = self.filterParams.is_build_filtered_out(
            valid=build["valid"],
            duration=build["duration"],
            issue_id=build["issue_id"],
            incident_test_id=incident_test_id,
        )
        return is_build_not_processed and not is_build_filtered_out

    def record_in_filter(
        self,
        record: Dict,
    ) -> bool:
        record_filter_out = self.filterParams.is_record_filtered_out(
            architecture=record["build__architecture"],
            compiler=record["build__compiler"],
            config_name=record["build__config_name"],
        )

        return not record_filter_out

    def test_in_filter(self, table_test: Literal["boot", "test"], record: Dict) -> bool:
        test_filter_pass = True

        status = record["status"]
        duration = record["duration"]
        path = record["path"]
        issue_id = record["incidents__issue__id"]
        incidents_test_id = record["incidents__test_id"]
        platform = env_misc_value_or_default(
            handle_environment_misc(record["environment_misc"])
        ).get("platform")

        if table_test == "boot":
            test_filter_pass = not self.filterParams.is_boot_filtered_out(
                status=status,
                duration=duration,
                path=path,
                issue_id=issue_id,
                incident_test_id=incidents_test_id,
                platform=platform,
            )
        else:
            test_filter_pass = not self.filterParams.is_test_filtered_out(
                status=status,
                duration=duration,
                path=path,
                issue_id=issue_id,
                incident_test_id=incidents_test_id,
                platform=platform,
            )

        return test_filter_pass

    def handle_test(self, record, tests):
        status = record["status"]

        tests["history"].append(get_history(record))
        tests["statusSummary"][status] += 1
        tests["configs"][record["build__config_name"]][status] += 1

        environment_misc = handle_environment_misc(record["environment_misc"])
        test_platform = env_misc_value_or_default(environment_misc).get("platform")
        tests["platforms"][test_platform][status] += 1

        if status == "ERROR" or status == "FAIL" or status == "MISS":
            tests["platformsFailing"].add(test_platform)
            tests["failReasons"][extract_error_message(record["misc"])] += 1

        archKey = f'{record["build__architecture"]}{record["build__compiler"]}'
        archSummary = tests["archSummary"].get(archKey)
        if not archSummary:
            archSummary = get_arch_summary(record)
            tests["archSummary"][archKey] = archSummary
        archSummary["status"][status] += 1

        update_issues(
            issue_id=record["incidents__issue__id"],
            issue_version=record["incidents__issue__version"],
            incident_test_id=record["incidents__test_id"],
            build_valid=record["build__valid"],
            issue_comment=record["incidents__issue__comment"],
            issue_report_url=record["incidents__issue__report_url"],
            task=tests,
            is_failed_task=status == STATUS_FAILED_VALUE,
            issue_from="test",
        )

    def get_filter_options(self, records, selected_trees, is_all_selected: bool):
        configs = set()
        archs = set()
        compilers = set()

        for r in records:
            current_tree = get_record_tree(r, selected_trees)
            if not current_tree or not is_record_tree_selected(
                r, current_tree, is_all_selected
            ):
                continue

            configs.add(r["build__config_name"])
            archs.add(r["build__architecture"])
            compilers.add(r["build__compiler"])

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
        processed_tests = set()
        tests = generate_test_dict()
        boots = generate_test_dict()
        compatibles: Set[str] = set()
        tree_status_summary = defaultdict(generate_tree_status_summary_dict)
        builds = {
            "items": [],
            "issues": {},
            "failedWithUnknownIssues": 0,
        }

        for record in records:
            try:
                validatedRecord = DefaultRecordValues(**record)
                record["status"] = validatedRecord.status
            except ValidationError:
                continue
            current_tree = get_record_tree(record, trees)
            if not current_tree:
                log_message(f"Tree not found for record: {record}")
                continue

            self._assign_default_record_values(record)

            if record["environment_compatible"] is not None:
                compatibles.update(record["environment_compatible"])

            tree_index = current_tree["index"]
            is_record_boot = is_boot(record['path'])
            # TODO -> Unify with tree_status_key, be careful with the pluralization
            test_filter_key = "boot" if is_record_boot else "test"

            build_id = record["build_id"]
            build = get_build(record, tree_index)

            record_tree_selected = is_record_tree_selected(
                record, current_tree, is_all_selected
            )

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

            should_process_test = (
                record['id'] is not None
                and self.test_in_filter(test_filter_key, record)
                and record["id"] not in processed_tests
            )

            if should_process_test:
                processed_tests.add(record["id"])
                self.handle_test(record, boots if is_record_boot else tests)

            should_process_build = self.build_in_filter(
                build=build,
                processed_builds=processed_builds,
                incident_test_id=record["incidents__test_id"],
            )

            processed_builds.add(build_id)
            if should_process_build:
                builds["items"].append(build)
                update_issues(
                    issue_id=record["incidents__issue__id"],
                    issue_version=record["incidents__issue__version"],
                    incident_test_id=record["incidents__test_id"],
                    build_valid=record["build__valid"],
                    issue_comment=record["incidents__issue__comment"],
                    issue_report_url=record["incidents__issue__report_url"],
                    task=builds,
                    is_failed_task=record["build__valid"] is not True,
                    issue_from="build",
                )

        builds["summary"] = create_details_build_summary(builds["items"])
        mutate_properties_to_list(builds, ["issues"])
        mutate_properties_to_list(tests, ["issues", "platformsFailing", "archSummary"])
        mutate_properties_to_list(boots, ["issues", "platformsFailing", "archSummary"])

        return (
            builds,
            tests,
            boots,
            tree_status_summary,
            list(compatibles),
        )

    def _assign_default_record_values(self, record: Dict) -> None:
        if record["build__architecture"] is None:
            record["build__architecture"] = UNKNOWN_STRING
        if record["build__compiler"] is None:
            record["build__compiler"] = UNKNOWN_STRING
        if record["build__config_name"] is None:
            record["build__config_name"] = UNKNOWN_STRING
        if (
            record["build__incidents__issue__id"] is None
            and record["build__valid"] is not True
        ):
            record["build__incidents__issue__id"] = UNKNOWN_STRING
        if (
            record["incidents__issue__id"] is None
            and record["status"] == STATUS_FAILED_VALUE
        ):
            record["incidents__issue__id"] = UNKNOWN_STRING

    def get_trees(
        self, hardware_id: str, origin: str, start_date: datetime, end_date: datetime
    ):
        # We need a subquery because if we filter by any hardware, it will get the
        # last head that has that hardware, but not the real head of the trees
        trees_subquery = get_tree_heads(origin, start_date, end_date)

        tree_id_fields = [
            "build__checkout__tree_name",
            "build__checkout__git_repository_branch",
            "build__checkout__git_repository_url",
        ]

        trees_query_set = (
            Tests.objects.filter(
                environment_compatible__contains=[hardware_id],
                origin=origin,
                build__checkout__start_time__lte=end_date,
                build__checkout__start_time__gte=start_date,
                build__checkout__git_commit_hash__in=Subquery(trees_subquery),
            )
            .values(
                *tree_id_fields,
                "build__checkout__git_commit_name",
                "build__checkout__git_commit_hash",
                "build__checkout__git_commit_tags",
            )
            .distinct(
                *tree_id_fields,
                "build__checkout__git_commit_hash",
            )
            .order_by(
                *tree_id_fields,
                "build__checkout__git_commit_hash",
                "-build__checkout__start_time",
            )
        )

        trees = []
        for idx, tree in enumerate(trees_query_set):
            trees.append(
                {
                    "treeName": tree["build__checkout__tree_name"],
                    "gitRepositoryBranch": tree[
                        "build__checkout__git_repository_branch"
                    ],
                    "gitRepositoryUrl": tree["build__checkout__git_repository_url"],
                    "headGitCommitName": tree["build__checkout__git_commit_name"],
                    "headGitCommitHash": tree["build__checkout__git_commit_hash"],
                    "headGitCommitTag": tree["build__checkout__git_commit_tags"],
                    "index": str(idx),
                }
            )

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

            selected.append(
                {
                    "tree_name": tree["treeName"],
                    "git_repository_branch": tree["gitRepositoryBranch"],
                    "git_repository_url": tree["gitRepositoryUrl"],
                    "index": tree["index"],
                    "git_commit_hash": displayed_commit,
                    "is_tree_selected": is_tree_selected,
                }
            )

        return selected

    def get_full_tests(
        self, *, hardware_id, origin, trees, start_date=int, end_date=int
    ):
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
            "incidents__issue__version",
            "incidents__issue__comment",
            "incidents__issue__report_url",
            "incidents__test_id",
            "build__incidents__issue__id",
            "build__incidents__issue__version",
        ).filter(
            start_time__gte=start_date,
            start_time__lte=end_date,
            build__checkout__origin=origin,
            environment_compatible__contains=[hardware_id],
            # TODO Treat commit_hash collision (it can happen between repos)
            build__checkout__git_commit_hash__in=commit_hashes,
        )
        return records

    # Using post to receive a body request
    def post(self, request, hardware_id):
        try:
            body = json.loads(request.body)

            post_body = PostBody(**body)

            origin = post_body.origin
            end_datetime = datetime.fromtimestamp(
                int(post_body.endTimestampInSeconds), timezone.utc
            )

            start_datetime = datetime.fromtimestamp(
                int(post_body.startTimestampInSeconds), timezone.utc
            )

            selected_commits = post_body.selectedCommits
            self.filterParams = FilterParams(body, process_body=True)
            self.setup_filters()

            is_all_selected = len(selected_commits) == 0
        except ValidationError as e:
            return create_error_response(e.json())
        except json.JSONDecodeError:
            return create_error_response(
                "Invalid body, request body must be a valid json string"
            )
        except (ValueError, TypeError):
            return create_error_response(
                "limitTimestampInSeconds must be a Unix Timestamp"
            )

        cache_params = {
            "hardware_id": hardware_id,
            "origin": origin,
            "selected_commits": json.dumps(selected_commits),
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
        }

        trees = getQueryCache(self.cache_key_get_tree_data, cache_params)

        if not trees:
            trees = self.get_trees(hardware_id, origin, start_datetime, end_datetime)
            setQueryCache(self.cache_key_get_tree_data, cache_params, trees)

        trees_with_selected_commits = self.get_trees_with_selected_commit(
            trees, selected_commits
        )

        params = {
            "hardware_id": hardware_id,
            "origin": origin,
            "trees": trees_with_selected_commits,
            "start_date": start_datetime,
            "end_date": end_datetime,
        }

        records = getQueryCache(self.cache_key_get_full_data, cache_params)

        if not records:
            records = self.get_full_tests(**params)
            setQueryCache(self.cache_key_get_full_data, params, records)

        if len(records) == 0:
            return create_error_response(
                error_message="Hardware not found", status_code=HTTPStatus.NOT_FOUND
            )

        builds, tests, boots, tree_status_summary, compatibles = self.sanitize_records(
            records, trees_with_selected_commits, is_all_selected
        )

        configs, archs, compilers = self.get_filter_options(
            records, trees_with_selected_commits, is_all_selected
        )

        trees_with_status_count = []
        for tree in trees:
            summary = tree_status_summary.get(tree["index"])
            trees_with_status_count.append(
                {**tree, "selectedCommitStatusSummary": summary}
            )

        return JsonResponse(
            {
                "builds": builds,
                "tests": tests,
                "boots": boots,
                "configs": configs,
                "archs": archs,
                "compilers": compilers,
                "trees": trees_with_status_count,
                "compatibles": compatibles,
            },
            safe=False,
        )
