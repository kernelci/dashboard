from kernelCI_app.helpers.database import dict_fetchall
from django.db import connections

from kernelCI_app.helpers.logger import log_message
from kernelCI_cache.typeModels.issues import IssueKeyTuple, UnsentIssueKeys


def get_unsent_issues() -> list[UnsentIssueKeys]:
    """Returns all issues that had no notification sent for and should not be ignored"""

    query = """
        SELECT
            N.issue_id,
            N.issue_version,
            N.issue_type
        FROM
            notifications_issue N
        WHERE
            N.notification_sent IS NULL
        """

    with connections["notifications"].cursor() as cursor:
        cursor.execute(query)
        results = dict_fetchall(cursor)

    try:
        valid_results: list[UnsentIssueKeys] = []
        for result in results:
            valid_results.append(
                UnsentIssueKeys(
                    issue_id=result["issue_id"],
                    issue_version=result["issue_version"],
                    issue_type=result["issue_type"],
                )
            )
    except ValueError as e:
        log_message(f"Validation error when getting all unsent issue keys: {e}")
        return []
    return valid_results


def get_all_issue_keys() -> list[IssueKeyTuple]:
    """Gets all the stored issue keys. Returns a list of tuples (issue_id, issue_version)."""
    query = """
        SELECT
            issue_id,
            issue_version
        FROM
            notifications_issue
    """

    with connections["notifications"].cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    try:
        valid_results: list[IssueKeyTuple] = []
        for result in results:
            valid_results.append(IssueKeyTuple(root=result))
    except ValueError as e:
        log_message(f"Validation error when getting all issue keys: {e}")
        return []

    return results
