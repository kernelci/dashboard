import json
from typing import Union, TypedDict, List, Optional, Dict
from django.utils import timezone
from datetime import timedelta

DEFAULT_QUERY_TIME_INTERVAL = {"days": 7}


class IncidentInfo(TypedDict):
    incidentsCount: int


class Issue(TypedDict):
    id: str
    comment: Optional[str]
    report_url: Optional[str]
    incidents_info: IncidentInfo


def create_issue(
    *, issue_id: str, issue_comment: Optional[str], issue_report_url: Optional[str]
) -> Issue:
    return {
        "id": issue_id,
        "comment": issue_comment,
        "report_url": issue_report_url,
        "incidents_info": {"incidentsCount": 1},
    }


def convert_issues_dict_to_list(issues_dict: Dict[str, Issue]) -> List[Issue]:
    return list(issues_dict.values())


def extract_platform(misc_environment: Union[str, dict, None]):
    parsedEnvMisc = None
    if isinstance(misc_environment, dict):
        parsedEnvMisc = misc_environment
    elif misc_environment is None:
        return "unknown"
    else:
        parsedEnvMisc = json.loads(misc_environment)
    platform = parsedEnvMisc.get("platform")
    if platform:
        return platform
    return "unknown"


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


def getErrorResponseBody(reason: str):
    return json.dumps({"error": True, "reason": reason})
