from kernelCI_app.constants.general import UNKNOWN_STRING
from typing import Set


def add_unfiltered_issue(
    *,
    issue_id: str,
    issue_version: int,
    should_increment: bool,
    issue_set: Set,
    is_invalid: bool
) -> None:
    if issue_id is not None and issue_version is not None and should_increment:
        issue_set.add((issue_id, issue_version))
    elif is_invalid is True:
        issue_set.add((UNKNOWN_STRING, None))
