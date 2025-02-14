from typing import Dict, Literal, Set

type PossibleTabs = Literal["build", "boot", "test"]


def add_unfiltered_issue(
    *,
    issue_id: str,
    issue_version: int,
    should_increment: bool,
    issue_set: Set,
    is_invalid: bool,
    unknown_issue_flag_dict: Dict[PossibleTabs, bool],
    unknown_issue_flag_tab: PossibleTabs,
) -> None:
    if issue_id is not None and issue_version is not None and should_increment:
        issue_set.add((issue_id, issue_version))
    elif is_invalid is True:
        unknown_issue_flag_dict[unknown_issue_flag_tab] = True
