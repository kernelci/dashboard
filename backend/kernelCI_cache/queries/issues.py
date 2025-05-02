from typing import Optional
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.helpers.logger import log_message
from kernelCI_cache.models import IssuesCustom
from kernelCI_cache.typeModels.databases import PossibleIssueType
from django.db import connections

from kernelCI_cache.typeModels.issuesCustom import CustomIssue


def get_unsent_issues() -> Optional[list[dict]]:
    """Returns all issues that had no notification sent for and should not be ignored"""

    query = """
        SELECT
            I.id,
            I.version,
            I.comment,
            I.type,
            I.kcidb_timestamp
        FROM
            issues_custom I
        LEFT JOIN
            notifications_issue N
        ON
            I.id = N.issue_id
            AND I.version = N.issue_version
        WHERE
            I.notification_ignore = FALSE
            AND N.notification_sent IS NULL
        """

    with connections["cache"].cursor() as cursor:
        cursor.execute(query)
        return dict_fetchall(cursor)


def assure_custom_issue_exists(
    *,
    id: str,
    version: int,
    kcidb_timestamp: str,
    comment: Optional[str],
    issue_type: PossibleIssueType,
    notification_ignore: bool = False,
) -> bool:
    """Tries to find an issue with that specific id and version.
    If it doesn't exist, creates a new one with the passed parameters"""
    try:
        IssuesCustom.objects.using("cache").get_or_create(
            id=id,
            version=version,
            defaults={
                "kcidb_timestamp": kcidb_timestamp,
                "comment": comment,
                "type": issue_type,
                "notification_ignore": notification_ignore,
            },
        )
        return True
    except Exception as e:
        log_message(f"Error creating custom issue:\n{e}")
        return False


def get_all_issue_keys() -> list[tuple[str, int]]:
    """Gets all the stored issue keys. Returns a list of tuples (issue_id, issue_version)."""
    query = """
        SELECT
            id,
            version
        FROM
            issues_custom
    """

    with connections["cache"].cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        return results


def update_custom_issues_batch(issues_data: list[CustomIssue]) -> bool:
    """Updates a list of issues in the cache database based on the provided list of CustomIssue.

    Returns True if all operations completed without major errors, False otherwise.
    """
    if not issues_data:
        return True

    try:
        for issue in issues_data:
            lookup_fields = {
                "id": issue.id,
                "version": issue.version,
            }

            update_fields = {
                "notification_ignore": issue.notification_ignore,
            }

            create_fields = {
                **update_fields,
                "kcidb_timestamp": issue.kcidb_timestamp,
                "comment": issue.comment,
                "type": issue.type,
            }

            try:
                IssuesCustom.objects.using("cache").update_or_create(
                    **lookup_fields,
                    defaults=update_fields,
                    create_defaults=create_fields,
                )
            except Exception as e:
                log_message(f"Error updating issue {issue.id}-{issue.version}: {e}")

        return True
    except Exception as e:
        log_message(f"Error updating issues in batch: {e}")
        return False
