from kernelCI_app.helpers.filters import UNKNOWN_STRING


def add_unfiltered_issue(
    *, issue_id, issue_version, should_increment, issue_set, is_invalid
):
    if issue_id is not None and issue_version is not None and should_increment:
        issue_set.add(issue_id)
    elif is_invalid is True:
        issue_set.add(UNKNOWN_STRING)
