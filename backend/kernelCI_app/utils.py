import json
from typing import Union, TypedDict, List, Optional, Dict
from django.utils import timezone
from datetime import timedelta

from kernelCI_app.helpers.logger import log_message

DEFAULT_QUERY_TIME_INTERVAL = {"days": 7}


class IncidentInfo(TypedDict):
    incidentsCount: int


class Issue(TypedDict):
    id: str
    version: str
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentInfo


def create_issue(
    *,
    issue_id: str,
    issue_version: str,
    issue_comment: Optional[str],
    issue_report_url: Optional[str]
) -> Issue:
    return {
        "id": issue_id,
        "version": issue_version,
        "comment": issue_comment,
        "report_url": issue_report_url,
        "incidents_info": {"incidentsCount": 1},
    }


def convert_issues_dict_to_list(issues_dict: Dict[str, Issue]) -> List[Issue]:
    return list(issues_dict.values())


# TODO misc is not stable and should be used as a POC only
def extract_error_message(misc: Union[str, dict, None]):
    parsedEnv = None
    if misc is None:
        return "unknown error"
    elif isinstance(misc, dict):
        parsedEnv = misc
    else:
        parsedEnv = json.loads(misc)
    error_message = parsedEnv.get("error_msg")
    if error_message:
        return error_message
    return "unknown error"


def getQueryTimeInterval(**kwargs):
    if not kwargs:
        return timezone.now() - timedelta(**DEFAULT_QUERY_TIME_INTERVAL)
    return timezone.now() - timedelta(**kwargs)


def getErrorResponseBody(reason: str) -> bytes:
    return json.dumps({"error": True, "reason": reason}).encode("utf-8")


def string_to_json(string: str) -> Optional[dict]:
    if (string):
        try:
            return json.loads(string)
        except json.JSONDecodeError as e:
            log_message(e.msg)
            return None


def is_boot(path: str | None) -> bool:
    return path is not None and (path == "boot" or path.startswith("boot."))
