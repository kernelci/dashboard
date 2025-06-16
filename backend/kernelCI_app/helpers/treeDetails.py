from collections.abc import Callable
from typing import Any, Optional, TypedDict
from kernelCI_app.constants.general import UNCATEGORIZED_STRING
from kernelCI_app.helpers.commonDetails import PossibleTabs, add_unfiltered_issue
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.commonDetails import BuildHistoryItem
from kernelCI_app.helpers.filters import (
    is_status_failure,
    should_increment_build_issue,
    should_increment_test_issue,
)
from kernelCI_app.helpers.build import build_status_map
from kernelCI_app.constants.general import UNKNOWN_STRING
from kernelCI_app.typeModels.databases import FAIL_STATUS, build_fail_status_list
from kernelCI_app.typeModels.issues import Issue, IssueDict
from kernelCI_app.utils import create_issue_typed, extract_error_message
from kernelCI_app.helpers.misc import (
    handle_build_misc,
    handle_environment_misc,
    build_misc_value_or_default,
    env_misc_value_or_default,
)
from kernelCI_app.utils import is_boot


class CheckoutWhereClauses(TypedDict):
    git_url_clause: Optional[str]
    git_branch_clause: str
    tree_name_clause: Optional[str]


def create_checkouts_where_clauses(
    git_url: Optional[str],
    git_branch: Optional[str],
    tree_name: Optional[str] = None,
) -> CheckoutWhereClauses:
    """Creates the SQL clauses for querying with url, branch and tree_name.

    If `tree_name` is not None, then that means that the endpoint where this is used
    could have been called without the url parameter (such as treeDetailsDirectView).
    In that case, the `git_url` parameter shouldn't compare it to NULL, because we can't
    tell if it is empty or was just not passed to the function.

    So if `tree_name` is not None, then `git_url_clause` will be None.
    """
    git_url_clause = """git_repository_url = %(git_url_param)s"""
    git_branch_clause = """git_repository_branch = %(git_branch_param)s"""
    tree_name_clause = "tree_name = %(tree_name)s" if tree_name else None

    if not git_url:
        git_url_clause = "git_repository_url IS NULL"

    if not git_branch:
        git_branch_clause = "git_repository_branch IS NULL"

    if tree_name and git_branch:
        git_url_clause = None

    return {
        "git_url_clause": git_url_clause,
        "git_branch_clause": git_branch_clause,
        "tree_name_clause": tree_name_clause,
    }


def get_current_row_data(current_row: dict) -> dict:
    tmp_test_env_comp_key = 12
    current_row_data = {
        "test_id": current_row[0],
        "test_origin": current_row[1],
        "test_environment_comment": current_row[2],
        "test_environment_misc": current_row[3],
        "test_path": current_row[4],
        "test_comment": current_row[5],
        "test_log_url": current_row[6],
        "test_status": current_row[7],
        "test_start_time": current_row[8],
        "test_duration": current_row[9],
        "test_number_value": current_row[10],
        "test_misc": current_row[11],
        "test_environment_compatible": current_row[tmp_test_env_comp_key],
        "build_id": current_row[13],
        "build_origin": current_row[14],
        "build_comment": current_row[15],
        "build_start_time": current_row[16],
        "build_duration": current_row[17],
        "build_architecture": current_row[18],
        "build_command": current_row[19],
        "build_compiler": current_row[20],
        "build_config_name": current_row[21],
        "build_config_url": current_row[22],
        "build_log_url": current_row[23],
        "build_status": current_row[24],
        "build_misc": current_row[25],
        "checkout_id": current_row[26],
        "checkout_git_repository_url": current_row[27],
        "checkout_git_repository_branch": current_row[28],
        "checkout_git_commit_tags": current_row[29],
        "checkout_origin": current_row[30],
        "incident_id": current_row[31],
        "incident_test_id": current_row[32],
        "incident_present": current_row[33],
        "issue_id": current_row[34],
        "issue_version": current_row[35],
        "issue_comment": current_row[36],
        "issue_report_url": current_row[37],
    }

    environment_misc = handle_environment_misc(
        current_row_data["test_environment_misc"]
    )
    current_row_data["test_platform"] = env_misc_value_or_default(environment_misc).get(
        "platform"
    )
    if current_row_data["test_status"] is None:
        current_row_data["test_status"] = "NULL"
    current_row_data["test_error"] = extract_error_message(
        current_row_data["test_misc"]
    )
    current_row_data["build_status"] = build_status_map(
        current_row_data["build_status"]
    ).upper()
    if current_row_data["test_environment_compatible"] is None:
        current_row_data["test_environment_compatible"] = UNKNOWN_STRING
    else:
        current_row_data["test_environment_compatible"] = current_row_data[
            "test_environment_compatible"
        ][0]
    if current_row_data["build_architecture"] is None:
        current_row_data["build_architecture"] = UNKNOWN_STRING
    if current_row_data["build_compiler"] is None:
        current_row_data["build_compiler"] = UNKNOWN_STRING
    if current_row_data["build_config_name"] is None:
        current_row_data["build_config_name"] = UNKNOWN_STRING
    if current_row_data["issue_id"] is None and (
        is_status_failure(current_row_data["build_status"], build_fail_status_list)
        or current_row_data["test_status"] == FAIL_STATUS
    ):
        current_row_data["issue_id"] = UNCATEGORIZED_STRING
    current_row_data["build_misc"] = handle_build_misc(current_row_data["build_misc"])
    if current_row_data["test_path"] is None:
        current_row_data["test_path"] = UNKNOWN_STRING

    current_row_data["history_item"] = {
        "id": current_row_data["test_id"],
        "origin": current_row_data["test_origin"],
        "status": current_row_data["test_status"],
        "duration": current_row_data["test_duration"],
        "path": current_row_data["test_path"],
        "start_time": current_row_data["test_start_time"],
        "environment_compatible": current_row[tmp_test_env_comp_key],
        "config": current_row_data["build_config_name"],
        "log_url": current_row_data["test_log_url"],
        "architecture": current_row_data["build_architecture"],
        "compiler": current_row_data["build_compiler"],
        "environment_misc": {"platform": current_row_data["test_platform"]},
    }

    return current_row_data


def process_tree_url(instance, row_data: dict) -> None:
    git_repository_url = row_data["checkout_git_repository_url"]
    if instance.tree_url == "" and git_repository_url is not None:
        instance.tree_url = git_repository_url


def call_based_on_compatible_and_misc_platform(
    row_data: dict, callback: Callable[[str], Any]
) -> Any:
    test_environment_compatible = row_data["test_environment_compatible"]
    test_environment_misc_platform = row_data["test_platform"]
    build_misc_platform = build_misc_value_or_default(row_data["build_misc"]).get(
        "platform"
    )

    if test_environment_compatible != UNKNOWN_STRING:
        return callback(test_environment_compatible)
    if test_environment_misc_platform != UNKNOWN_STRING:
        return callback(test_environment_misc_platform)
    return callback(build_misc_platform)


def get_hardware_filter(row_data: dict) -> Any:
    test_environment_compatible = row_data["test_environment_compatible"]
    hardware_filter = test_environment_compatible
    hardware_filter = call_based_on_compatible_and_misc_platform(row_data, lambda x: x)
    return hardware_filter


def get_build(row_data: dict) -> BuildHistoryItem:
    return BuildHistoryItem(
        id=row_data["build_id"],
        origin=row_data["build_origin"],
        architecture=row_data["build_architecture"],
        config_name=row_data["build_config_name"],
        misc=row_data["build_misc"],
        config_url=row_data["build_config_url"],
        compiler=row_data["build_compiler"],
        valid=row_data["build_status"],
        duration=row_data["build_duration"],
        log_url=row_data["build_log_url"],
        start_time=row_data["build_start_time"],
        git_repository_url=row_data["checkout_git_repository_url"],
        git_repository_branch=row_data["checkout_git_repository_branch"],
    )


def process_builds_issue(*, instance, row_data) -> None:
    build_id = row_data["build_id"]
    issue_id = row_data["issue_id"]
    issue_comment = row_data["issue_comment"]
    issue_report_url = row_data["issue_report_url"]
    issue_version = row_data["issue_version"]
    build_status = row_data["build_status"]
    incident_test_id = row_data["incident_test_id"]

    (issue_id, issue_version, can_insert_issue) = should_increment_build_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
        build_status=build_status,
    )

    if issue_id and issue_version is not None and can_insert_issue:
        table: IssueDict = instance.build_issues_dict
        current_issue: Issue = table.get((issue_id, issue_version))
        if current_issue:
            current_issue.incidents_info.increment(build_status)
        else:
            table[(issue_id, issue_version)] = create_issue_typed(
                issue_id=issue_id,
                issue_version=issue_version,
                issue_comment=issue_comment,
                issue_report_url=issue_report_url,
                starting_count_status=build_status,
            )

    elif build_id not in instance.processed_builds and build_status == FAIL_STATUS:
        instance.failed_builds_with_unknown_issues += 1


def process_tests_issue(*, instance, row_data, is_boot=False) -> None:
    test_status = row_data["test_status"]
    issue_id = row_data["issue_id"]
    issue_comment = row_data["issue_comment"]
    issue_version = row_data["issue_version"]
    issue_report_url = row_data["issue_report_url"]
    incident_test_id = row_data["incident_test_id"]

    (issue_id, issue_version, can_insert_issue) = should_increment_test_issue(
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )

    if issue_id and issue_version is not None and can_insert_issue:
        if is_boot:
            table: IssueDict = instance.boot_issues_dict
        else:
            table: IssueDict = instance.test_issues_dict

        current_issue: Issue = table.get((issue_id, issue_version))
        if current_issue:
            current_issue.incidents_info.increment(test_status)
        else:
            table[(issue_id, issue_version)] = create_issue_typed(
                issue_id=issue_id,
                issue_version=issue_version,
                issue_comment=issue_comment,
                issue_report_url=issue_report_url,
                starting_count_status=test_status,
            )
    elif test_status == FAIL_STATUS:
        if is_boot:
            instance.failed_boots_with_unknown_issues += 1
        else:
            instance.failed_tests_with_unknown_issues += 1


def decide_if_is_build_filtered_out(instance, row_data):
    issue_id = row_data["issue_id"]
    issue_version = row_data["issue_version"]
    build_status = row_data["build_status"]
    build_duration = row_data["build_duration"]
    incident_test_id = row_data["incident_test_id"]
    build_origin = row_data["build_origin"]

    is_build_filtered_out = instance.filters.is_build_filtered_out(
        build_status=build_status,
        duration=build_duration,
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
        build_origin=build_origin,
    )
    return is_build_filtered_out


def decide_if_is_boot_filtered_out(instance, row_data):
    test_status = row_data["test_status"]
    test_duration = row_data["test_duration"]
    issue_id = row_data["issue_id"]
    issue_version = row_data["issue_version"]
    test_path = row_data["test_path"]
    incident_test_id = row_data["incident_test_id"]
    origin = row_data["test_origin"]

    return instance.filters.is_boot_filtered_out(
        duration=test_duration,
        issue_id=issue_id,
        issue_version=issue_version,
        path=test_path,
        status=test_status,
        incident_test_id=incident_test_id,
        origin=origin,
    )


def decide_if_is_full_row_filtered_out(instance, row_data):
    hardware_filter = get_hardware_filter(row_data)

    return instance.filters.is_record_filtered_out(
        hardwares=[hardware_filter],
        architecture=row_data["build_architecture"],
        compiler=row_data["build_compiler"],
        config_name=row_data["build_config_name"],
    )


def decide_if_is_test_filtered_out(instance, row_data):
    test_status = row_data["test_status"]
    test_duration = row_data["test_duration"]
    issue_id = row_data["issue_id"]
    issue_version = row_data["issue_version"]
    test_path = row_data["test_path"]
    incident_test_id = row_data["incident_test_id"]
    origin = row_data["test_origin"]

    return instance.filters.is_test_filtered_out(
        duration=test_duration,
        issue_id=issue_id,
        issue_version=issue_version,
        path=test_path,
        status=test_status,
        incident_test_id=incident_test_id,
        origin=origin,
    )


def increment_test_origin_summary(
    test_origin: str,
    test_status: str,
    origin_summary: dict[str, StatusCount],
):
    if origin_summary.get(test_origin) is None:
        origin_summary[test_origin] = StatusCount()
    setattr(
        origin_summary[test_origin],
        test_status,
        getattr(origin_summary[test_origin], test_status) + 1,
    )


def process_test_summary(instance, row_data):
    test_status = row_data["test_status"]
    build_config = row_data["build_config_name"]
    build_arch = row_data["build_architecture"]
    build_compiler = row_data["build_compiler"]
    test_platform = row_data["test_platform"]
    test_error = row_data["test_error"]
    test_environment_compatible = row_data["test_environment_compatible"]

    instance.testStatusSummary[test_status] = (
        instance.testStatusSummary.get(test_status, 0) + 1
    )

    arch_key = "%s-%s" % (build_arch, build_compiler)
    arch_summary = instance.test_arch_summary.get(
        arch_key,
        {"arch": build_arch, "compiler": build_compiler, "status": {}},
    )
    arch_summary["status"][test_status] = arch_summary["status"].get(test_status, 0) + 1
    instance.test_arch_summary[arch_key] = arch_summary

    config_summary = instance.test_configs.get(build_config, {})
    config_summary[test_status] = config_summary.get(test_status, 0) + 1
    instance.test_configs[build_config] = config_summary

    if is_status_failure(test_status):
        instance.testPlatformsWithErrors.add(test_platform)
        instance.testFailReasons[test_error] = (
            instance.testFailReasons.get(test_error, 0) + 1
        )

    if test_environment_compatible != UNKNOWN_STRING:
        instance.testEnvironmentCompatible[test_environment_compatible][
            test_status
        ] += 1
    else:
        instance.testEnvironmentMisc[test_platform][test_status] += 1

    increment_test_origin_summary(
        test_origin=row_data["test_origin"],
        test_status=test_status,
        origin_summary=instance.test_summary["origins"],
    )


def process_boots_summary(instance, row_data):
    test_status = row_data["test_status"]
    build_config = row_data["build_config_name"]
    build_arch = row_data["build_architecture"]
    build_compiler = row_data["build_compiler"]
    test_platform = row_data["test_platform"]
    test_error = row_data["test_error"]
    test_environment_compatible = row_data["test_environment_compatible"]

    instance.bootStatusSummary[test_status] = (
        instance.bootStatusSummary.get(test_status, 0) + 1
    )

    arch_key = "%s-%s" % (build_arch, build_compiler)
    arch_summary = instance.bootArchSummary.get(
        arch_key,
        {"arch": build_arch, "compiler": build_compiler, "status": {}},
    )
    arch_summary["status"][test_status] = arch_summary["status"].get(test_status, 0) + 1
    instance.bootArchSummary[arch_key] = arch_summary

    config_summary = instance.bootConfigs.get(build_config, {})
    config_summary[test_status] = config_summary.get(test_status, 0) + 1
    instance.bootConfigs[build_config] = config_summary

    if is_status_failure(test_status):
        instance.bootPlatformsFailing.add(test_platform)
        instance.bootFailReasons[test_error] = (
            instance.bootFailReasons.get(test_error, 0) + 1
        )

    if test_environment_compatible != UNKNOWN_STRING:
        instance.bootEnvironmentCompatible[test_environment_compatible][
            test_status
        ] += 1
    else:
        instance.bootEnvironmentMisc[test_platform][test_status] += 1

    increment_test_origin_summary(
        test_origin=row_data["test_origin"],
        test_status=test_status,
        origin_summary=instance.boot_summary["origins"],
    )


def process_filters(instance, row_data: dict) -> None:
    issue_id = row_data["issue_id"]
    issue_version = row_data["issue_version"]
    incident_test_id = row_data["incident_test_id"]
    build_status = row_data["build_status"]

    if row_data["build_id"] is not None:
        instance.global_configs.add(row_data["build_config_name"])
        instance.global_architectures.add(row_data["build_architecture"])
        instance.global_compilers.add(row_data["build_compiler"])
        instance.unfiltered_origins["build"].add(row_data["build_origin"])

        build_issue_id, build_issue_version, is_build_issue = (
            should_increment_build_issue(
                issue_id=issue_id,
                issue_version=issue_version,
                incident_test_id=incident_test_id,
                build_status=build_status,
            )
        )

        is_failed_build = build_status == FAIL_STATUS
        add_unfiltered_issue(
            issue_id=build_issue_id,
            issue_version=build_issue_version,
            should_increment=is_build_issue,
            issue_set=instance.unfiltered_build_issues,
            unknown_issue_flag_dict=instance.unfiltered_uncategorized_issue_flags,
            unknown_issue_flag_tab="build",
            is_failed_task=is_failed_build,
        )

    if row_data["test_id"] is not None:
        test_issue_id, test_issue_version, is_test_issue = should_increment_test_issue(
            issue_id=issue_id,
            issue_version=issue_version,
            incident_test_id=incident_test_id,
        )

        if is_boot(row_data["test_path"]):
            issue_set = instance.unfiltered_boot_issues
            origin_set = instance.unfiltered_origins["boot"]
            flag_tab: PossibleTabs = "boot"
        else:
            issue_set = instance.unfiltered_test_issues
            origin_set = instance.unfiltered_origins["test"]
            flag_tab: PossibleTabs = "test"

        is_failed_test = row_data["test_status"] == FAIL_STATUS
        add_unfiltered_issue(
            issue_id=test_issue_id,
            issue_version=test_issue_version,
            should_increment=is_test_issue,
            issue_set=issue_set,
            is_failed_task=is_failed_test,
            unknown_issue_flag_dict=instance.unfiltered_uncategorized_issue_flags,
            unknown_issue_flag_tab=flag_tab,
        )

        origin_set.add(row_data["test_origin"])
