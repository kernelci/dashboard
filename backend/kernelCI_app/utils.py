import json
from typing import Union, List, Optional
from django.utils import timezone
from datetime import timedelta

from kernelCI_app.constants.general import DEFAULT_INTERVAL_IN_DAYS
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.databases import DatabaseStatusValues
from kernelCI_app.typeModels.issues import Issue, IssueDict

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


def is_boot(path: str | None) -> bool:
    return path is not None and (path == "boot" or path.startswith("boot."))


def validate_str_to_dict(value):
    if isinstance(value, str):
        return json.loads(value)
    return value
