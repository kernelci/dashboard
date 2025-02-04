import json
from typing import Union, List, Optional, Dict
import typing_extensions
from django.utils import timezone
from datetime import timedelta

from kernelCI_app.helpers.logger import log_message
from kernelCI_app.typeModels.issues import IncidentInfo, Issue

DEFAULT_QUERY_TIME_INTERVAL = {"days": 7}


def create_issue(
    *,
    issue_id: str,
    issue_version: int,
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


@typing_extensions.deprecated(
    'The `convert_issues_dict_to_list` method is deprecated; use `convert_issues_dict_to_list_typed` '
    'and use type validation.',
)
def convert_issues_dict_to_list(issues_dict: Dict[str, Issue]) -> List[Issue]:
    return list(issues_dict.values())


def convert_issues_dict_to_list_typed(*, issues_dict_list: Dict) -> List[Issue]:
    issues: List[Issue] = []
    for issue in issues_dict_list.values():
        issues.append(
            Issue(
                id=issue["id"],
                version=issue["version"],
                comment=issue["comment"],
                report_url=issue["report_url"],
                incidents_info=IncidentInfo(
                    incidentsCount=issue["incidents_info"]["incidentsCount"],
                ),
            )
        )
    return issues


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
