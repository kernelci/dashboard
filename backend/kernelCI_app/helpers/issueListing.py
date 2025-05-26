from typing import Optional

from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.typeModels.issues import (
    CULPRIT_CODE,
    CULPRIT_HARNESS,
    CULPRIT_TOOL,
    HAS_INCIDENT_OPTION,
    IssueFilterOptions,
    PossibleIssueCulprits,
)


def should_discard_issue_by_culprit(
    *, culprit_filters: set[PossibleIssueCulprits], record: dict
) -> bool:
    """Returns true if the record should be discarted from the resulting set of records"""

    if not culprit_filters:
        return False

    if record["culprit_code"] is True and CULPRIT_CODE in culprit_filters:
        return False
    if record["culprit_harness"] is True and CULPRIT_HARNESS in culprit_filters:
        return False
    if record["culprit_tool"] is True and CULPRIT_TOOL in culprit_filters:
        return False

    return True  # Discards if has filter but all the culprits are None


def should_discard_issue_by_origin(
    *, origin_filters: set[str], issue_origin: str
) -> bool:
    if not origin_filters:
        return False

    if issue_origin not in origin_filters:
        return True

    return False


def should_discard_issue_by_options(
    *, option_filters: set[IssueFilterOptions], record: dict
) -> bool:
    if not option_filters:
        return False

    if HAS_INCIDENT_OPTION in option_filters and record["has_incident"] is True:
        return False

    return True


def should_discard_issue_by_category(
    *, categories_filters: set[str], issue_categories: Optional[list[str]]
):
    if not categories_filters:
        return False

    if not issue_categories:
        return True

    for category in issue_categories:
        if category in categories_filters:
            return False

    return True


def should_discard_issue_record(
    *, filters: Optional[FilterParams] = None, issue: dict
) -> bool:
    if not filters:
        return False

    origin_filters = filters.filter_origins
    culprit_filters = filters.filter_issue_culprits
    option_filters = filters.filter_issue_options
    categories_filters = filters.filter_issue_categories

    issue_origin = issue["origin"]
    issue_categories = issue.get("categories")

    if (
        should_discard_issue_by_culprit(culprit_filters=culprit_filters, record=issue)
        or should_discard_issue_by_origin(
            origin_filters=origin_filters, issue_origin=issue_origin
        )
        or should_discard_issue_by_options(option_filters=option_filters, record=issue)
        or should_discard_issue_by_category(
            categories_filters=categories_filters, issue_categories=issue_categories
        )
    ):
        return True

    return False
