from collections.abc import Callable
from typing import Any, Optional, TypedDict
from kernelCI_app.helpers.commonDetails import add_unfiltered_issue
from kernelCI_app.helpers.filters import (
    is_test_failure,
    should_increment_build_issue,
    should_increment_test_issue,
    UNKNOWN_STRING,
)
from kernelCI_app.typeModels.databases import FAIL_STATUS
from kernelCI_app.utils import (
    extract_error_message,
    create_issue,
)
from kernelCI_app.helpers.misc import (
    handle_build_misc,
    handle_environment_misc,
    build_misc_value_or_default,
    env_misc_value_or_default,
)
from kernelCI_app.cache import getQueryCache, setQueryCache
from kernelCI_app.utils import is_boot
from django.db import connection


class CheckoutWhereClauses(TypedDict):
    git_url_clause: str
    git_branch_clause: str


def create_checkouts_where_clauses(
    git_url: Optional[str], git_branch: Optional[str]
) -> CheckoutWhereClauses:
    git_url_clause = """git_repository_url = %(git_url_param)s"""
    git_branch_clause = """git_repository_branch = %(git_branch_param)s"""

    if not git_url:
        git_url_clause = "git_repository_url IS NULL"

    if not git_branch:
        git_branch_clause = "git_repository_branch IS NULL"

    return {"git_url_clause": git_url_clause, "git_branch_clause": git_branch_clause}


def get_tree_details_data(request, commit_hash):
    cache_key = "treeDetails"

    origin_param = request.GET.get("origin")
    git_url_param = request.GET.get("git_url")
    git_branch_param = request.GET.get("git_branch")

    params = {
        "commit_hash": commit_hash,
        "origin_param": origin_param,
        "git_url_param": git_url_param,
        "git_branch_param": git_branch_param,
    }

    rows = getQueryCache(cache_key, params)
    if rows is None:
        checkout_clauses = create_checkouts_where_clauses(
            git_url=git_url_param, git_branch=git_branch_param
        )

        git_url_clause = checkout_clauses.get("git_url_clause")
        git_branch_clause = checkout_clauses.get("git_branch_clause")

        query = f"""
        SELECT
                tests.build_id AS tests_build_id,
                tests.id AS tests_id,
                tests.origin AS tests_origin,
                tests.environment_comment AS tests_environment_comment,
                tests.environment_misc AS tests_environment_misc,
                tests.path AS tests_path,
                tests.comment AS tests_comment,
                tests.log_url AS tests_log_url,
                tests.status AS tests_status,
                tests.waived AS tests_waived,
                tests.start_time AS tests_start_time,
                tests.duration AS tests_duration,
                tests.number_value AS tests_number_value,
                tests.misc AS tests_misc,
                tests.environment_compatible AS tests_environment_compatible,
                builds_filter.*,
                incidents.id AS incidents_id,
                incidents.test_id AS incidents_test_id,
                incidents.present AS incidents_present,
                issues.id AS issues_id,
                issues.version AS issues_version,
                issues.comment AS issues_comment,
                issues.report_url AS issues_report_url
        FROM
            (
                SELECT
                    builds.checkout_id AS builds_checkout_id,
                    builds.id AS builds_id,
                    builds.comment AS builds_comment,
                    builds.start_time AS builds_start_time,
                    builds.duration AS builds_duration,
                    builds.architecture AS builds_architecture,
                    builds.command AS builds_command,
                    builds.compiler AS builds_compiler,
                    builds.config_name AS builds_config_name,
                    builds.config_url AS builds_config_url,
                    builds.log_url AS builds_log_url,
                    builds.valid AS builds_valid,
                    builds.misc AS builds_misc,
                    tree_head.*
                FROM
                    (
                        SELECT
                            checkouts.id AS checkout_id,
                            checkouts.git_repository_url AS checkouts_git_repository_url,
                            checkouts.git_repository_branch AS checkouts_git_repository_branch,
                            checkouts.git_commit_tags
                        FROM
                            checkouts
                        WHERE
                            checkouts.git_commit_hash = %(commit_hash)s AND
                            {git_url_clause} AND
                            {git_branch_clause} AND
                            checkouts.origin = %(origin_param)s
                    ) AS tree_head
                INNER JOIN builds
                    ON tree_head.checkout_id = builds.checkout_id
                WHERE
                    builds.origin = %(origin_param)s
            ) AS builds_filter
        LEFT JOIN tests
            ON builds_filter.builds_id = tests.build_id
        LEFT JOIN incidents
            ON tests.id = incidents.test_id OR
               builds_filter.builds_id = incidents.build_id
        LEFT JOIN issues
            ON incidents.issue_id = issues.id
            AND incidents.issue_version = issues.version
        WHERE
            tests.origin = %(origin_param)s OR
            tests.origin IS NULL
        """
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            setQueryCache(cache_key, params, rows)

    return rows


def get_current_row_data(current_row: dict) -> dict:
    tmp_test_env_comp_key = 14
    current_row_data = {
        "test_id": current_row[1],
        "test_origin": current_row[2],
        "test_environment_comment": current_row[3],
        "test_environment_misc": current_row[4],
        "test_path": current_row[5],
        "test_comment": current_row[6],
        "test_log_url": current_row[7],
        "test_status": current_row[8],
        "test_waived": current_row[9],
        "test_start_time": current_row[10],
        "test_duration": current_row[11],
        "test_number_value": current_row[12],
        "test_misc": current_row[13],
        "test_environment_compatible": current_row[tmp_test_env_comp_key],
        "build_id": current_row[16],
        "build_comment": current_row[17],
        "build_start_time": current_row[18],
        "build_duration": current_row[19],
        "build_architecture": current_row[20],
        "build_command": current_row[21],
        "build_compiler": current_row[22],
        "build_config_name": current_row[23],
        "build_config_url": current_row[24],
        "build_log_url": current_row[25],
        "build_valid": current_row[26],
        "build_misc": current_row[27],
        "checkout_id": current_row[28],
        "checkout_git_repository_url": current_row[29],
        "checkout_git_repository_branch": current_row[30],
        "checkout_git_commit_tags": current_row[31],
        "incident_id": current_row[32],
        "incident_test_id": current_row[33],
        "incident_present": current_row[34],
        "issue_id": current_row[35],
        "issue_version": current_row[36],
        "issue_comment": current_row[37],
        "issue_report_url": current_row[38],
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
        current_row_data["build_valid"] is False
        or current_row_data["build_valid"] is None
        or current_row_data["test_status"] == FAIL_STATUS
    ):
        current_row_data["issue_id"] = UNKNOWN_STRING
    current_row_data["build_misc"] = handle_build_misc(current_row_data["build_misc"])
    if current_row_data["test_path"] is None:
        current_row_data["test_path"] = UNKNOWN_STRING

    current_row_data["history_item"] = {
        "id": current_row_data["test_id"],
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


def is_test_boots_test(row_data: dict) -> bool:
    test_path = row_data["test_path"]
    return is_boot(test_path)


def get_build(row_data: dict) -> dict:
    return {
        "id": row_data["build_id"],
        "architecture": row_data["build_architecture"],
        "config_name": row_data["build_config_name"],
        "misc": row_data["build_misc"],
        "config_url": row_data["build_config_url"],
        "compiler": row_data["build_compiler"],
        "valid": row_data["build_valid"],
        "duration": row_data["build_duration"],
        "log_url": row_data["build_log_url"],
        "start_time": row_data["build_start_time"],
        "git_repository_url": row_data["checkout_git_repository_url"],
        "git_repository_branch": row_data["checkout_git_repository_branch"],
    }


def process_builds_issue(instance, row_data):
    build_id = row_data["build_id"]
    issue_id = row_data["issue_id"]
    issue_comment = row_data["issue_comment"]
    issue_report_url = row_data["issue_report_url"]
    issue_version = row_data["issue_version"]
    build_valid = row_data["build_valid"]
    incident_test_id = row_data["incident_test_id"]

    (issue_id, can_insert_issue) = should_increment_build_issue(
        issue_id=issue_id,
        incident_test_id=incident_test_id,
        build_valid=build_valid,
    )

    if issue_id and issue_version is not None and can_insert_issue:
        current_issue = instance.processed_build_issues.get((issue_id, issue_version))
        if current_issue:
            current_issue["incidents_info"]["incidentsCount"] += 1
        else:
            instance.processed_build_issues[(issue_id, issue_version)] = create_issue(
                issue_id=issue_id,
                issue_comment=issue_comment,
                issue_report_url=issue_report_url,
                issue_version=issue_version,
            )

    elif build_id not in instance.processed_builds and build_valid is False:
        instance.failed_builds_with_unknown_issues += 1


def process_tests_issue(instance, row_data):
    test_status = row_data["test_status"]
    issue_id = row_data["issue_id"]
    issue_comment = row_data["issue_comment"]
    issue_version = row_data["issue_version"]
    issue_report_url = row_data["issue_report_url"]
    incident_test_id = row_data["incident_test_id"]

    (issue_id, can_insert_issue) = should_increment_test_issue(
        issue_id, incident_test_id
    )

    if issue_id and issue_version is not None and can_insert_issue:
        currentIssue = instance.testIssuesTable.get((issue_id, issue_version))
        if currentIssue:
            currentIssue["incidents_info"]["incidentsCount"] += 1
        else:
            instance.testIssuesTable[(issue_id, issue_version)] = create_issue(
                issue_id=issue_id,
                issue_version=issue_version,
                issue_comment=issue_comment,
                issue_report_url=issue_report_url,
            )
    elif test_status == FAIL_STATUS:
        instance.failedTestsWithUnknownIssues += 1


def process_boots_issue(instance, row_data):
    test_status = row_data["test_status"]
    issue_id = row_data["issue_id"]
    issue_comment = row_data["issue_comment"]
    issue_version = row_data["issue_version"]
    issue_report_url = row_data["issue_report_url"]
    incident_test_id = row_data["incident_test_id"]

    (issue_id, can_insert_issue) = should_increment_test_issue(
        issue_id=issue_id, incident_test_id=incident_test_id
    )

    if issue_id and issue_version is not None and can_insert_issue:
        currentIssue = instance.bootsIssuesTable.get((issue_id, issue_version))
        if currentIssue:
            currentIssue["incidents_info"]["incidentsCount"] += 1
        else:
            instance.bootsIssuesTable[(issue_id, issue_version)] = create_issue(
                issue_id=issue_id,
                issue_version=issue_version,
                issue_comment=issue_comment,
                issue_report_url=issue_report_url,
            )
    elif test_status == FAIL_STATUS:
        instance.failedBootsWithUnknownIssues += 1


def decide_if_is_build_filtered_out(instance, row_data):
    issue_id = row_data["issue_id"]
    issue_version = row_data["issue_version"]
    build_valid = row_data["build_valid"]
    build_duration = row_data["build_duration"]
    incident_test_id = row_data["incident_test_id"]

    is_build_filtered_out = instance.filters.is_build_filtered_out(
        valid=build_valid,
        duration=build_duration,
        issue_id=issue_id,
        issue_version=issue_version,
        incident_test_id=incident_test_id,
    )
    return is_build_filtered_out


def decide_if_is_boot_filtered_out(instance, row_data):
    test_status = row_data["test_status"]
    test_duration = row_data["test_duration"]
    issue_id = row_data["issue_id"]
    issue_version = row_data["issue_version"]
    test_path = row_data["test_path"]
    incident_test_id = row_data["incident_test_id"]

    return instance.filters.is_boot_filtered_out(
        duration=test_duration,
        issue_id=issue_id,
        issue_version=issue_version,
        path=test_path,
        status=test_status,
        incident_test_id=incident_test_id,
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
    testPath = row_data["test_path"]
    incident_test_id = row_data["incident_test_id"]

    return instance.filters.is_test_filtered_out(
        duration=test_duration,
        issue_id=issue_id,
        path=testPath,
        status=test_status,
        incident_test_id=incident_test_id,
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

    if is_test_failure(test_status):
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

    archKey = "%s-%s" % (build_arch, build_compiler)
    archSummary = instance.bootArchSummary.get(
        archKey,
        {"arch": build_arch, "compiler": build_compiler, "status": {}},
    )
    archSummary["status"][test_status] = archSummary["status"].get(test_status, 0) + 1
    instance.bootArchSummary[archKey] = archSummary

    configSummary = instance.bootConfigs.get(build_config, {})
    configSummary[test_status] = configSummary.get(test_status, 0) + 1
    instance.bootConfigs[build_config] = configSummary

    if is_test_failure(test_status):
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


def process_filters(instance, row_data: dict) -> None:
    issue_id = row_data["issue_id"]
    issue_version = row_data["issue_version"]
    incident_test_id = row_data["incident_test_id"]
    build_valid = row_data["build_valid"]

    if row_data["build_id"] is not None:
        instance.global_configs.add(row_data["build_config_name"])
        instance.global_architectures.add(row_data["build_architecture"])
        instance.global_compilers.add(row_data["build_compiler"])

        build_issue_id, is_build_issue = should_increment_build_issue(
            issue_id=issue_id,
            incident_test_id=incident_test_id,
            build_valid=build_valid,
        )

        is_invalid = build_valid is False
        add_unfiltered_issue(
            issue_id=build_issue_id,
            issue_version=issue_version,
            should_increment=is_build_issue,
            issue_set=instance.unfiltered_build_issues,
            is_invalid=is_invalid,
        )

    if row_data["test_id"] is not None:
        test_issue_id, is_test_issue = should_increment_test_issue(
            issue_id=issue_id,
            incident_test_id=incident_test_id,
        )

        if is_boot(row_data["test_path"]):
            issue_set = instance.unfiltered_boot_issues
        else:
            issue_set = instance.unfiltered_test_issues

        is_invalid = row_data["test_status"] == FAIL_STATUS
        add_unfiltered_issue(
            issue_id=test_issue_id,
            issue_version=issue_version,
            should_increment=is_test_issue,
            issue_set=issue_set,
            is_invalid=is_invalid,
        )
