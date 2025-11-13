import json
import os
from typing import Union, List, Optional
from django.utils import timezone
from datetime import timedelta

import yaml

from kernelCI_app.constants.general import DEFAULT_INTERVAL_IN_DAYS
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.typeModels.common import GroupedStatus, StatusCount
from kernelCI_app.typeModels.databases import DatabaseStatusValues
from kernelCI_app.typeModels.issues import Issue, IssueDict
from kernelCI_app.typeModels.treeListing import TestStatusCount

DEFAULT_QUERY_TIME_INTERVAL = {"days": DEFAULT_INTERVAL_IN_DAYS}


def create_issue_typed(
    *,
    issue_id: str,
    issue_version: int,
    issue_comment: Optional[str],
    issue_report_url: Optional[str],
    starting_count_status: Optional[DatabaseStatusValues],
) -> Issue:
    incident_count = StatusCount()
    incident_count.increment(starting_count_status)
    return Issue(
        id=issue_id,
        version=issue_version,
        comment=issue_comment,
        report_url=issue_report_url,
        incidents_info=incident_count,
    )


def convert_issues_dict_to_list_typed(*, issues_dict: IssueDict) -> List[Issue]:
    issues: List[Issue] = []
    for issue in issues_dict.values():
        if isinstance(issue, dict):
            issues.append(
                Issue(
                    id=issue["id"],
                    version=issue["version"],
                    comment=issue["comment"],
                    report_url=issue["report_url"],
                    incidents_info=StatusCount(**issue["incidents_info"]),
                )
            )
        else:
            issues.append(issue)
    return issues


# TODO misc is not stable and should be used as a POC only
def extract_error_message(misc: Union[str, dict, None]):
    parsed_env = None
    if misc is None:
        return "unknown error"
    elif isinstance(misc, dict):
        parsed_env = misc
    else:
        parsed_env = json.loads(misc)
    error_message = parsed_env.get("error_msg")
    if error_message:
        return error_message
    return "unknown error"


def get_query_time_interval(**kwargs):
    if not kwargs:
        return timezone.now() - timedelta(**DEFAULT_QUERY_TIME_INTERVAL)
    return timezone.now() - timedelta(**kwargs)


def get_error_body_response(reason: str) -> bytes:
    return json.dumps({"error": True, "reason": reason}).encode("utf-8")


def string_to_json(string: str) -> Optional[dict]:
    if string:
        try:
            return json.loads(string)
        except json.JSONDecodeError as e:
            log_message(e.msg)
            return None


def sanitize_dict(maybe_dict: Union[str, dict, None]) -> Optional[dict]:
    """
    Corrects data to always be either None or a dict.
    If data is a string, it attempts to parse it as JSON.

    Returns None or the data as a dict.
    """

    if maybe_dict is None or isinstance(maybe_dict, dict):
        return maybe_dict

    if isinstance(maybe_dict, str):
        return string_to_json(maybe_dict)

    return None


def is_boot(path: str | None) -> bool:
    return path is not None and (path == "boot" or path.startswith("boot."))


def validate_str_to_dict(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def group_status(count: Union[StatusCount, TestStatusCount]) -> GroupedStatus:
    result: GroupedStatus = {"success": 0, "failed": 0, "inconclusive": 0}
    if isinstance(count, StatusCount):
        result["success"] = count.PASS
        result["failed"] = count.FAIL
        result["inconclusive"] = (
            count.ERROR + count.SKIP + count.MISS + count.DONE + count.NULL
        )
    elif isinstance(count, TestStatusCount):
        result["success"] = count.pass_count
        result["failed"] = count.fail_count
        result["inconclusive"] = (
            count.error_count
            + count.skip_count
            + count.miss_count
            + count.done_count
            + count.null_count
        )
    else:
        log_message("group_status only accepts StatusCount or TestStatusCount types")
    return result


def read_yaml_file(*, base_dir, file):
    """Reads a YAML file and returns the data as a dictionary."""
    filepath = os.path.join(base_dir, file)
    try:
        with open(filepath, "r") as file:
            data = yaml.safe_load(
                file
            )  # Use safe_load to avoid potential security issues
            return data
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")
        return None
    except Exception as exc:
        print(f"Error reading YAML file: {exc}")
        return None
