from collections import defaultdict
from datetime import datetime, timezone
import json
from typing import Dict, List, Literal, Optional, Set

from kernelCI_app.cache import getQueryCache, setQueryCache
from kernelCI_app.constants.hardwareDetails import (
    SELECTED_HEAD_TREE_VALUE,
)
from kernelCI_app.helpers.build import build_status_map
from kernelCI_app.helpers.commonDetails import add_unfiltered_issue
from kernelCI_app.helpers.filters import (
    UNKNOWN_STRING,
    FilterParams,
    is_test_failure,
    should_increment_build_issue,
    should_increment_test_issue,
)
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.helpers.misc import env_misc_value_or_default, handle_environment_misc
from kernelCI_app.helpers.trees import get_tree_heads
from kernelCI_app.models import Tests
from kernelCI_app.typeModels.databases import FAIL_STATUS, NULL_STATUS
from kernelCI_app.typeModels.commonDetails import (
    BuildArchitectures,
    BuildStatusCount,
    BuildSummary,
    Misc,
    TestArchSummaryItem,
    TestStatusCount,
    TestSummary,
)
from kernelCI_app.typeModels.hardwareDetails import (
    DefaultRecordValues,
    HardwareBuildHistoryItem,
    HardwareTestHistoryItem,
    HardwareDetailsPostBody,
    Tree,
)
from kernelCI_app.utils import (
    convert_issues_dict_to_list_typed,
    create_issue,
    extract_error_message,
    is_boot,
)
from django.db import models
from pydantic import ValidationError
from django.db.models import Subquery
from kernelCI_app.typeModels.hardwareDetails import (
    PossibleTestType,
)


def unstable_parse_post_body(*, instance, request) -> None:
    body = json.loads(request.body)

    post_body = HardwareDetailsPostBody(**body)

    instance.origin = post_body.origin
    instance.end_datetime = datetime.fromtimestamp(
        int(post_body.endTimestampInSeconds), timezone.utc
    )

    instance.start_datetime = datetime.fromtimestamp(
        int(post_body.startTimestampInSeconds), timezone.utc
    )

    instance.selected_commits = post_body.selectedCommits

    instance.filters = FilterParams(body, process_body=True)


def get_hardware_trees_data(
    *,
    hardware_id: str,
    origin: str,
    selected_commits: Dict[str, str],
    start_datetime: datetime,
    end_datetime: datetime,
) -> List[Tree]:
    cache_key = "hardwareDetailsTreeData"

    trees_cache_params = {
        "hardware_id": hardware_id,
        "origin": origin,
        "selected_commits": json.dumps(selected_commits),
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
    }

    trees: List[Tree] = getQueryCache(cache_key, trees_cache_params)

    if not trees:
        # We need a subquery because if we filter by any hardware, it will get the
        # last head that has that hardware, but not the real head of the trees
        trees_subquery = get_tree_heads(origin, start_datetime, end_datetime)

        tree_id_fields = [
            "build__checkout__tree_name",
            "build__checkout__git_repository_branch",
            "build__checkout__git_repository_url",
        ]

        trees_query_set = (
            Tests.objects.filter(
                models.Q(environment_compatible__contains=[hardware_id])
                | models.Q(environment_misc__platform=hardware_id),
                origin=origin,
                build__checkout__start_time__lte=end_datetime,
                build__checkout__start_time__gte=start_datetime,
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
                Tree(
                    index=str(idx),
                    tree_name=tree["build__checkout__tree_name"],
                    git_repository_branch=tree[
                        "build__checkout__git_repository_branch"
                    ],
                    git_repository_url=tree["build__checkout__git_repository_url"],
                    head_git_commit_name=tree["build__checkout__git_commit_name"],
                    head_git_commit_hash=tree["build__checkout__git_commit_hash"],
                    head_git_commit_tag=tree["build__checkout__git_commit_tags"],
                    selected_commit_status=None,
                    is_selected=None,
                )
            )

        setQueryCache(cache_key, trees_cache_params, trees)

    return trees


def set_trees_status_summary(
    *, trees: List[Tree], tree_status_summary: defaultdict
) -> None:
    for tree in trees:
        summary = tree_status_summary.get(tree.index)
        tree.selected_commit_status = summary


def get_displayed_commit(*, tree: Tree, selected_commit: Optional[str]):
    if (not selected_commit) or (selected_commit == SELECTED_HEAD_TREE_VALUE):
        return tree.head_git_commit_hash
    return selected_commit


def get_trees_with_selected_commit(
    *, trees: List[Tree], selected_commits: Dict[str, str]
) -> List[Tree]:
    selected: List[Tree] = []

    for tree in trees:
        tree_idx = tree.index

        raw_selected_commit = selected_commits.get(tree_idx)

        is_tree_selected = raw_selected_commit is not None

        displayed_commit = get_displayed_commit(
            tree=tree, selected_commit=raw_selected_commit
        )

        selected.append(
            Tree(
                index=tree.index,
                tree_name=tree.tree_name,
                git_repository_branch=tree.git_repository_branch,
                git_repository_url=tree.git_repository_url,
                head_git_commit_name=tree.head_git_commit_name,
                head_git_commit_hash=displayed_commit,
                head_git_commit_tag=tree.head_git_commit_tag,
                selected_commit_status=tree.selected_commit_status,
                is_selected=is_tree_selected,
            )
        )

    return selected


def get_hardware_details_data(
    *,
    hardware_id: str,
    origin: str,
    trees_with_selected_commits: List[Tree],
    start_datetime: datetime,
    end_datetime: datetime,
):
    cache_key = "hardwareDetailsFullData"

    tests_cache_params = {
        "hardware_id": hardware_id,
        "origin": origin,
        "trees": trees_with_selected_commits,
        "start_date": start_datetime,
        "end_date": end_datetime,
    }

    records = getQueryCache(cache_key, tests_cache_params)

    if not records:
        records = query_records(
            hardware_id=hardware_id,
            origin=origin,
            trees=trees_with_selected_commits,
            start_date=start_datetime,
            end_date=end_datetime,
        )
        setQueryCache(cache_key, tests_cache_params, records)

    return records


def query_records(
    *, hardware_id: str, origin: str, trees: List[Tree], start_date=int, end_date=int
):
    commit_hashes = [tree.head_git_commit_hash for tree in trees]

    return Tests.objects.values(
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
        models.Q(environment_compatible__contains=[hardware_id])
        | models.Q(environment_misc__platform=hardware_id),
        start_time__gte=start_date,
        start_time__lte=end_date,
        build__checkout__origin=origin,
        # TODO Treat commit_hash collision (it can happen between repos)
        build__checkout__git_commit_hash__in=commit_hashes,
    )


# deprecated, use get_arch_summary_typed
def get_arch_summary(record: Dict) -> Dict:
    return {
        "arch": record["build__architecture"],
        "compiler": record["build__compiler"],
        "status": defaultdict(int),
    }


def get_arch_summary_typed(record: Dict) -> TestArchSummaryItem:
    return TestArchSummaryItem(
        arch=record["build__architecture"],
        compiler=record["build__compiler"],
        status=TestStatusCount(),
    )


# deprecated, use get_build_typed
def get_build(record: Dict, tree_idx: int) -> Dict:
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


def get_build_typed(record: Dict, tree_idx: int) -> HardwareBuildHistoryItem:
    return HardwareBuildHistoryItem(
        id=record["build_id"],
        architecture=record["build__architecture"],
        config_name=record["build__config_name"],
        misc=record["build__misc"],
        config_url=record["build__config_url"],
        compiler=record["build__compiler"],
        valid=record["build__valid"],
        duration=record["build__duration"],
        log_url=record["build__log_url"],
        start_time=record["build__start_time"],
        git_repository_url=record["build__checkout__git_repository_url"],
        git_repository_branch=record["build__checkout__git_repository_branch"],
        tree_index=tree_idx,
        tree_name=record["build__checkout__tree_name"],
        issue_id=record["build__incidents__issue__id"],
        issue_version=record["build__incidents__issue__version"],
    )


def get_tree_key(record: Dict) -> str:
    return (
        record["build__checkout__tree_name"]
        + record["build__checkout__git_repository_branch"]
        + record["build__checkout__git_repository_url"]
    )


def get_history(record: Dict):
    return {
        "id": record["id"],
        "status": record["status"],
        "path": record["path"],
        "duration": record["duration"],
        "start_time": record["start_time"],
        "environment_compatible": record["environment_compatible"],
        "config": record["build__config_name"],
        "log_url": record["log_url"],
        "architecture": record["build__architecture"],
        "compiler": record["build__compiler"],
        "misc": {"platform": record["test_platform"]},
    }


def get_validated_current_tree(
    *, record: Dict, selected_trees: List[Tree]
) -> Optional[Tree]:
    # TODO: combine DefaultRecordValues and assign_default_record_values into either one or the other
    try:
        validated_record = DefaultRecordValues(**record)
        record["status"] = validated_record.status
    except ValidationError:
        log_message(f"Invalid row status for {record}")
        return None

    current_tree = get_current_record_tree_in_selection(
        record=record, selected_trees=selected_trees
    )

    if not current_tree:
        log_message(f"Tree not found for record: {record}")
        return None

    return current_tree


def get_current_record_tree_in_selection(
    *, record: Dict, selected_trees: List[Tree]
) -> Optional[Tree]:
    current_tree_name = record["build__checkout__tree_name"]
    current_tree_branch = record["build__checkout__git_repository_branch"]
    current_tree_url = record["build__checkout__git_repository_url"]

    for tree in selected_trees:
        if (
            current_tree_name == tree.tree_name
            and current_tree_branch == tree.git_repository_branch
            and current_tree_url == tree.git_repository_url
        ):
            return tree

    return None


def generate_test_dict() -> Dict[str, any]:
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


def generate_build_summary_typed() -> BuildSummary:
    return BuildSummary(
        status=BuildStatusCount(),
        architectures={},
        configs={},
        issues=[],
        unknown_issues=0,
    )


def generate_test_summary_typed() -> TestSummary:
    return TestSummary(
        status=TestStatusCount(),
        architectures=[],
        configs={},
        issues=[],
        unknown_issues=0,
        fail_reasons={},
        failed_platforms=set(),
    )


def generate_tree_status_summary_dict() -> Dict[str, defaultdict[int]]:
    return {
        "builds": defaultdict(int),
        "boots": defaultdict(int),
        "tests": defaultdict(int),
    }


# Status Summary should be unaffected by filters because it is placed above filters in the UI
def handle_tree_status_summary(
    *,
    record: Dict,
    tree_status_summary: Dict[str, str],
    tree_index: str,
    processed_builds: Set[str],
) -> None:
    is_record_boot = is_boot(path=record["path"])
    test_type_key = "boots" if is_record_boot else "tests"
    tree_status_summary[tree_index][test_type_key][record["status"]] += 1

    if record["build_id"] not in processed_builds:
        build_status = build_status_map.get(record["build__valid"])
        tree_status_summary[tree_index]["builds"][build_status] += 1


def create_record_test_platform(*, record: Dict) -> str:
    environment_misc = handle_environment_misc(record["environment_misc"])
    test_platform = env_misc_value_or_default(environment_misc).get("platform")
    record["test_platform"] = test_platform

    return test_platform


# deprecated, use handle_test_history and handle_test_summary separately instead, with typing
def handle_test_or_boot(record: Dict, task: Dict) -> None:
    status = record["status"]

    test_platform = create_record_test_platform(record=record)

    task["history"].append(get_history(record))
    task["statusSummary"][status] += 1
    task["configs"][record["build__config_name"]][status] += 1

    task["platforms"][test_platform][status] += 1

    if is_test_failure(status):
        task["platformsFailing"].add(test_platform)
        task["failReasons"][extract_error_message(record["misc"])] += 1

    archKey = f'{record["build__architecture"]}{record["build__compiler"]}'
    archSummary = task["archSummary"].get(archKey)
    if not archSummary:
        archSummary = get_arch_summary(record)
        task["archSummary"][archKey] = archSummary
    archSummary["status"][status] += 1

    update_issues(
        issue_id=record["incidents__issue__id"],
        issue_version=record["incidents__issue__version"],
        incident_test_id=record["incidents__test_id"],
        build_valid=record["build__valid"],
        issue_comment=record["incidents__issue__comment"],
        issue_report_url=record["incidents__issue__report_url"],
        task=task,
        is_failed_task=status == FAIL_STATUS,
        issue_from="test",
    )


def handle_test_history(
    *,
    record: Dict,
    task: List[HardwareTestHistoryItem],
) -> None:
    create_record_test_platform(record=record)

    test_history_item = HardwareTestHistoryItem(
        id=record["id"],
        status=record["status"],
        duration=record["duration"],
        path=record["path"],
        start_time=record["start_time"],
        environment_compatible=record["environment_compatible"],
        config=record["build__config_name"],
        log_url=record["log_url"],
        architecture=record["build__architecture"],
        compiler=record["build__compiler"],
        misc=Misc(platform=record["test_platform"]),
        tree_name=record["build__checkout__tree_name"],
        git_repository_branch=record["build__checkout__git_repository_branch"],
    )

    task.append(test_history_item)


def handle_test_summary(
    *,
    record: Dict,
    task: TestSummary,
    processed_issues: Dict,
    processed_archs: Dict[str, TestArchSummaryItem],
) -> None:
    status = record["status"]

    if status is None:
        status = NULL_STATUS

    setattr(task.status, status, getattr(task.status, status) + 1)

    config_name = record["build__config_name"]
    if task.configs.get(config_name) is None:
        task.configs[config_name] = TestStatusCount()
    setattr(
        task.configs[config_name],
        status,
        getattr(task.configs[config_name], status) + 1,
    )

    environment_misc = handle_environment_misc(record["environment_misc"])
    test_platform = env_misc_value_or_default(environment_misc).get("platform")
    if task.platforms is None:
        task.platforms = {}
    if task.platforms.get(test_platform) is None:
        task.platforms[test_platform] = TestStatusCount()
    setattr(
        task.platforms[test_platform],
        status,
        getattr(task.platforms[test_platform], status) + 1,
    )

    if is_test_failure(status):
        task.failed_platforms.add(test_platform)
        task.fail_reasons[extract_error_message(record["misc"])] += 1

    arch_key = f'{record["build__architecture"]}{record["build__compiler"]}'
    arch_summary = processed_archs.get(arch_key)
    if not arch_summary:
        arch_summary = get_arch_summary_typed(record)
        processed_archs[arch_key] = arch_summary
    setattr(arch_summary.status, status, getattr(arch_summary.status, status) + 1)

    process_issue(record=record, task_issues_dict=processed_issues, issue_from="test")


def handle_build_history(*, record: Dict, tree_idx: int, builds: List[HardwareBuildHistoryItem]) -> None:
    build = get_build_typed(record=record, tree_idx=tree_idx)
    builds.append(build)


def handle_build_summary(
    *,
    record: Dict,
    builds_summary: BuildSummary,
    processed_issues: Dict,
    tree_index: int,
) -> None:
    build: HardwareBuildHistoryItem = get_build_typed(record, tree_idx=tree_index)

    # TODO: use build_status_map values or BuildStatusCount keys
    status_key: Literal["valid", "invalid", "null"] = build_status_map.get(build.valid)
    setattr(
        builds_summary.status,
        status_key,
        getattr(builds_summary.status, status_key) + 1,
    )

    if config := build.config_name:
        build_config_summary = builds_summary.configs.get(config)
        if not build_config_summary:
            build_config_summary = BuildStatusCount()
            builds_summary.configs[config] = build_config_summary
        setattr(
            builds_summary.configs[config],
            status_key,
            getattr(builds_summary.configs[config], status_key) + 1,
        )

    if arch := build.architecture:
        build_arch_summary = builds_summary.architectures.get(arch)
        if not build_arch_summary:
            build_arch_summary = BuildArchitectures()
            builds_summary.architectures[arch] = build_arch_summary
        setattr(
            builds_summary.architectures[arch],
            status_key,
            getattr(builds_summary.architectures[arch], status_key) + 1,
        )

        compiler = build.compiler
        if (
            compiler is not None
            and compiler not in builds_summary.architectures.get(arch).compilers
        ):
            builds_summary.architectures[arch].compilers.append(compiler)

    process_issue(record=record, task_issues_dict=processed_issues, issue_from="build")


# deprecated, use handle_build_history and handle_build_summary separately instead, with typing
def handle_build(*, instance, record: Dict, build: Dict) -> None:
    instance.builds["items"].append(build)
    update_issues(
        issue_id=record["incidents__issue__id"],
        issue_version=record["incidents__issue__version"],
        incident_test_id=record["incidents__test_id"],
        build_valid=record["build__valid"],
        issue_comment=record["incidents__issue__comment"],
        issue_report_url=record["incidents__issue__report_url"],
        task=instance.builds,
        is_failed_task=record["build__valid"] is not True,
        issue_from="build",
    )


def process_issue(
    *, record, task_issues_dict: Dict, issue_from: Literal["build", "test"]
) -> None:
    if issue_from == "build":
        is_failed_task = record["build__valid"] is not True
    else:
        is_failed_task = record["status"] == FAIL_STATUS

    update_issues(
        issue_id=record["incidents__issue__id"],
        issue_version=record["incidents__issue__version"],
        incident_test_id=record["incidents__test_id"],
        build_valid=record["build__valid"],
        issue_comment=record["incidents__issue__comment"],
        issue_report_url=record["incidents__issue__report_url"],
        is_failed_task=is_failed_task,
        issue_from=issue_from,
        task=task_issues_dict,
    )


# TODO unify with treeDetails
def update_issues(
    *,
    issue_id: Optional[str],
    issue_version: Optional[int],
    incident_test_id: Optional[str],
    build_valid: Optional[bool],
    issue_comment: Optional[str],
    issue_report_url: Optional[str],
    task: Dict,
    is_failed_task: bool,
    issue_from: Literal["build", "test"],
) -> None:
    can_insert_issue = True
    if issue_from == "build":
        (issue_id, can_insert_issue) = should_increment_build_issue(
            issue_id=issue_id,
            incident_test_id=incident_test_id,
            build_valid=build_valid,
        )
    elif issue_from == "test":
        (issue_id, can_insert_issue) = should_increment_test_issue(
            issue_id, incident_test_id
        )

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


def decide_if_is_full_record_filtered_out(
    *,
    instance,
    record: Dict,
    current_tree: Tree,
    is_all_selected: bool,
) -> bool:
    is_current_tree_selected = is_record_tree_selected(
        record=record, tree=current_tree, is_all_selected=is_all_selected
    )
    if not is_current_tree_selected:
        return True

    is_record_filtered_out_result = instance.filters.is_record_filtered_out(
        hardwares=record["environment_compatible"],
        architecture=record["build__architecture"],
        compiler=record["build__compiler"],
        config_name=record["build__config_name"],
    )

    return is_record_filtered_out_result


def decide_if_is_build_in_filter(
    *,
    instance,
    build: Dict,
    processed_builds: Set[str],
    incident_test_id: Optional[str],
) -> bool:
    is_build_not_processed = build["id"] not in processed_builds
    is_build_filtered_out_result = instance.filters.is_build_filtered_out(
        valid=build["valid"],
        duration=build["duration"],
        issue_id=build["issue_id"],
        issue_version=build["issue_version"],
        incident_test_id=incident_test_id,
    )
    return is_build_not_processed and not is_build_filtered_out_result


def decide_if_is_test_in_filter(
    *, instance, test_type: PossibleTestType, record: Dict, processed_tests: Set[str]
) -> bool:
    is_test_processed = record["id"] in processed_tests
    if is_test_processed:
        return False

    test_filter_pass = True

    status = record["status"]
    duration = record["duration"]
    path = record["path"]
    issue_id = record["incidents__issue__id"]
    issue_version = record["incidents__issue__version"]
    incidents_test_id = record["incidents__test_id"]
    platform = env_misc_value_or_default(
        handle_environment_misc(record["environment_misc"])
    ).get("platform")

    if test_type == "boot":
        test_filter_pass = not instance.filters.is_boot_filtered_out(
            status=status,
            duration=duration,
            path=path,
            issue_id=issue_id,
            issue_version=issue_version,
            incident_test_id=incidents_test_id,
            platform=platform,
        )
    else:
        test_filter_pass = not instance.filters.is_test_filtered_out(
            status=status,
            duration=duration,
            path=path,
            issue_id=issue_id,
            issue_version=issue_version,
            incident_test_id=incidents_test_id,
            platform=platform,
        )

    return test_filter_pass


def get_filter_options(
    *, instance, records: List[Dict], selected_trees: List[Tree], is_all_selected: bool
) -> None:
    for record in records:
        current_tree = get_current_record_tree_in_selection(
            record=record, selected_trees=selected_trees
        )
        if not current_tree or not is_record_tree_selected(
            record=record, tree=current_tree, is_all_selected=is_all_selected
        ):
            continue

        process_filters(instance=instance, record=record)


def process_filters(*, instance, record: Dict) -> None:
    incident_test_id = record["incidents__test_id"]

    if record["build_id"] is not None:
        build_issue_id = record["build__incidents__issue__id"]
        build_issue_version = record["build__incidents__issue__version"]
        build_valid = record["build__valid"]

        instance.global_configs.add(record["build__config_name"])
        instance.global_architectures.add(record["build__architecture"])
        instance.global_compilers.add(record["build__compiler"])

        build_issue_id, is_build_issue = should_increment_build_issue(
            issue_id=build_issue_id,
            incident_test_id=incident_test_id,
            build_valid=build_valid,
        )

        is_invalid = build_valid is False
        add_unfiltered_issue(
            issue_id=build_issue_id,
            issue_version=build_issue_version,
            should_increment=is_build_issue,
            issue_set=instance.unfiltered_build_issues,
            is_invalid=is_invalid,
        )

    if record["id"] is not None:
        if is_boot(record["path"]):
            issue_set = instance.unfiltered_boot_issues
            platform_set = instance.unfiltered_boot_platforms
        else:
            issue_set = instance.unfiltered_test_issues
            platform_set = instance.unfiltered_test_platforms

        test_issue_id = record["incidents__issue__id"]
        test_issue_version = record["incidents__issue__version"]
        test_issue_id, is_test_issue = should_increment_test_issue(
            issue_id=test_issue_id,
            incident_test_id=incident_test_id,
        )

        is_invalid = record["status"] == FAIL_STATUS
        add_unfiltered_issue(
            issue_id=test_issue_id,
            issue_version=test_issue_version,
            should_increment=is_test_issue,
            issue_set=issue_set,
            is_invalid=is_invalid,
        )

        environment_misc = handle_environment_misc(record["environment_misc"])
        test_platform = env_misc_value_or_default(environment_misc).get("platform")
        platform_set.add(test_platform)


def is_record_tree_selected(*, record, tree: Tree, is_all_selected: bool) -> bool:
    if is_all_selected:
        return True
    return (
        tree.is_selected is not None
        and tree.is_selected
        and tree.head_git_commit_hash == record["build__checkout__git_commit_hash"]
    )


def mutate_properties_to_list(dict: Dict, keys: List[str]) -> None:
    for key in keys:
        value = dict[key]
        if isinstance(value, Dict):
            dict[key] = list(value.values())
        elif isinstance(value, Set):
            dict[key] = list(value)


def assign_default_record_values(record: Dict) -> None:
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
    if record["incidents__issue__id"] is None and record["status"] == FAIL_STATUS:
        record["incidents__issue__id"] = UNKNOWN_STRING


def format_issue_summary_for_response(
    *,
    builds_summary: BuildSummary,
    boots_summary: TestSummary,
    tests_summary: TestSummary,
    processed_issues: Dict,
) -> None:
    builds_summary.issues = convert_issues_dict_to_list_typed(
        issues_dict=processed_issues["build"]["issues"]
    )
    boots_summary.issues = convert_issues_dict_to_list_typed(
        issues_dict=processed_issues["boot"]["issues"]
    )
    tests_summary.issues = convert_issues_dict_to_list_typed(
        issues_dict=processed_issues["test"]["issues"]
    )
    builds_summary.unknown_issues = processed_issues["build"]["failedWithUnknownIssues"]
    boots_summary.unknown_issues = processed_issues["boot"]["failedWithUnknownIssues"]
    tests_summary.unknown_issues = processed_issues["test"]["failedWithUnknownIssues"]
