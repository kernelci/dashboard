from django.http import JsonResponse
from django.views import View
from kernelCI_app.helpers.filters import (
    should_increment_test_issue,
    UNKNOWN_STRING,
    FilterParams,
)
from kernelCI_app.utils import (
    convert_issues_dict_to_list,
    extract_error_message,
    create_issue,
    IncidentInfo,
)
from kernelCI_app.helpers.misc import (
    handle_build_misc,
    handle_environment_misc,
    build_misc_value_or_default,
    env_misc_value_or_default
)
from kernelCI_app.cache import getQueryCache, setQueryCache
from django.db import connection
from collections import defaultdict

from kernelCI_app.viewCommon import create_details_build_summary

def get_tree_details_data(request, commit_hash):
    cache_key = "treeDetailsSlow"

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
        query = """
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
                            checkouts.git_repository_branch AS checkouts_git_repository_branch
                        FROM
                            checkouts
                        WHERE
                            checkouts.git_commit_hash = %(commit_hash)s AND
                            checkouts.git_repository_url = %(git_url_param)s AND
                            checkouts.git_repository_branch = %(git_branch_param)s AND
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
        WHERE
            tests.origin = %(origin_param)s OR
            tests.origin IS NULL
        """
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            setQueryCache(cache_key, params, rows)

        return rows



def get_current_row_data(current_row):
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
        "incident_id": current_row[31],
        "incident_test_id": current_row[32],
        "incident_present": current_row[33],
        "issue_id": current_row[34],
        "issue_comment": current_row[35],
        "issue_report_url": current_row[36],
    }

    environment_misc = handle_environment_misc(
        current_row_data["test_environment_misc"]
    )
    current_row_data["test_platform"] = env_misc_value_or_default(
        environment_misc
    ).get("platform")
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
        or current_row_data["test_status"] == "FAIL"
    ):
        current_row_data["issue_id"] = UNKNOWN_STRING
    current_row_data["build_misc"] = handle_build_misc(current_row_data["build_misc"])
    if current_row_data["test_path"] is None:
        current_row_data["test_path"] = UNKNOWN_STRING

    current_row_data["history_item"] = {
        "id": current_row_data["test_id"],
        "status": current_row_data["test_status"],
        "duration": current_row_data["test_duration"],
        "startTime": current_row_data["test_start_time"],
        "hardware": current_row[tmp_test_env_comp_key],
    }

    return current_row_data


def get_tree_url(row_data, current_tree_url: str) -> str:
        git_repository_url = row_data["checkout_git_repository_url"]
        if current_tree_url == "" and git_repository_url is not None:
            return git_repository_url

def call_based_on_compatible_and_misc_platform(row_data, callback):
    test_environment_compatible = row_data["test_environment_compatible"]
    test_environment_misc_platform = row_data["test_platform"]
    build_misc_platform = build_misc_value_or_default(
        row_data["build_misc"]
    ).get("platform", UNKNOWN_STRING)

    if test_environment_compatible != UNKNOWN_STRING:
        return callback(test_environment_compatible)
    if test_environment_misc_platform != UNKNOWN_STRING:
        return callback(test_environment_misc_platform)
    return callback(build_misc_platform)

def get_hardware_filter(row_data):
    test_environment_compatible = row_data["test_environment_compatible"]
    hardware_filter = test_environment_compatible
    hardware_filter = call_based_on_compatible_and_misc_platform(row_data, lambda x: x)
    return hardware_filter

def is_test_boots_test(row_data):
    test_path = row_data["test_path"]
    if test_path.startswith("boot"):
        return True
    return False

def get_build(row_data):
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
    build_valid = row_data["build_valid"]

    if issue_id and (build_valid is False or build_valid is None):
        current_issue = instance.processed_build_issues.get(issue_id)
        if current_issue:
            current_issue["incidents_info"]["incidentsCount"] += 1
        else:
            instance.processed_build_issues[issue_id] = create_issue(
                issue_id=row_data["issue_id"],
                issue_comment=row_data["issue_comment"],
                issue_report_url=row_data["issue_report_url"],
            )
    elif build_id not in instance.processed_builds and build_valid is False:
        instance.failed_builds_with_unknown_issues += 1

    if build_id in instance.processed_builds:
        return
    instance.processed_builds.add(build_id)
    instance.builds.append(get_build(row_data))


def decide_if_is_build_filtered_out(instance, row_data):
    issue_id = row_data["issue_id"]
    build_valid = row_data["build_valid"]
    build_duration = row_data["build_duration"]

    is_build_filtered_out = instance.filters.is_build_filtered_out(
        valid=build_valid, duration=build_duration, issue_id=issue_id
    )
    return is_build_filtered_out

def decide_if_is_boot_filtered_out(instance, row_data):
    testStatus = row_data["test_status"]
    testDuration = row_data["test_duration"]
    issue_id = row_data["issue_id"]
    testPath = row_data["test_path"]
    incident_test_id = row_data["incident_test_id"]

    is_boot_filter_out = instance.filters.is_boot_filtered_out(
        duration=testDuration,
        issue_id=issue_id,
        path=testPath,
        status=testStatus,
        incident_test_id=incident_test_id,
    )

    return is_boot_filter_out

def decide_if_is_full_row_filtered_out(instance, row_data):
    hardware_filter = get_hardware_filter(row_data)

    instance.filters.is_record_filtered_out(
                    hardwares=[hardware_filter],
                    architecture=row_data["build_architecture"],
                    compiler=row_data["build_compiler"],
                    config_name=row_data["build_config_name"],
                )

