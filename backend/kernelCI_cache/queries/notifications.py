import json

from django.db import connections
from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.management.commands.helpers.summary import ReportConfigs, TreeKey
from kernelCI_cache.typeModels.databases import PossibleIssueType
from kernelCI_cache.utils import get_current_timestamp_kcidb_format
from kernelCI_cache.models import NotificationsCheckout, NotificationsIssue
from kernelCI_app.helpers.logger import log_message


RESEND_INTERVAL = "12 hours"
"""The time interval where a report can be resent.

 Meaning that if a report was sent now, it must wait this value until it can be sent again"""


def mark_checkout_notification_as_sent(
    *,
    msg_id: str,
    checkout_id: str,
    git_repository_branch: str,
    git_repository_url: str,
    origin: str,
    path: str,
) -> bool:
    try:
        timestamp = get_current_timestamp_kcidb_format()
        NotificationsCheckout.objects.using("notifications").create(
            notification_message_id=msg_id,
            notification_sent=timestamp,
            checkout_id=checkout_id,
            git_repository_branch=git_repository_branch,
            git_repository_url=git_repository_url,
            origin=origin,
            path=path,
        )
        return True
    except Exception as e:
        print(f"Error storing notification checkout: {e}")
        return False


def mark_issue_notification_sent(
    *,
    msg_id: str,
    issue_id: str,
    issue_version: int,
    issue_type: PossibleIssueType,
) -> bool:
    """Creates an entry for an issue notification"""
    try:
        timestamp = get_current_timestamp_kcidb_format()
        NotificationsIssue.objects.using("notifications").update_or_create(
            issue_id=issue_id,
            issue_version=issue_version,
            issue_type=issue_type,
            defaults={
                "notification_message_id": msg_id,
                "notification_sent": timestamp,
            },
        )
        return True
    except Exception as e:
        log_message(f"Error marking issue notification sent:\n{e}")
        return False


def mark_issue_notification_not_sent(
    *,
    issue_id: str,
    issue_version: int,
    issue_type: PossibleIssueType,
) -> bool:
    """Creates an entry for an issue without notifications

    Returns:
      True if an issue already exists in the database, or was created.

      False if any exception occurs
    """
    try:
        issue_exists = (
            NotificationsIssue.objects.using("notifications")
            .filter(
                issue_id=issue_id,
                issue_version=issue_version,
            )
            .exists()
        )

        if not issue_exists:
            NotificationsIssue.objects.using("notifications").create(
                issue_id=issue_id,
                issue_version=issue_version,
                issue_type=issue_type,
            )
        return True
    except Exception as e:
        log_message(f"Error marking issue notification not sent:\n{e}")
        return False


def check_sent_notifications(
    tree_prop_map: dict[TreeKey, ReportConfigs],
) -> list[TreeKey]:
    """
    Queries the notification_checkout table to see
    which of the current reports (represented by the tree_prop_map)
    can be sent again.

    Returns:
        A list of tuples containing the TreeKeys of the reports that were already sent.
    """
    if not tree_prop_map:
        return []

    checkouts_for_checking: list[tuple[str, str, str, str]] = []
    for tree_props in tree_prop_map.values():
        for prop in tree_props:
            prop_path = prop.get("path")
            # For our purposes, a unique report is defined by these fields
            checkouts_for_checking.append(
                (
                    prop.get("branch"),
                    prop.get("giturl"),
                    prop.get("origin", DEFAULT_ORIGIN),
                    json.dumps(prop_path) if prop_path else "%",
                )
            )

    if not checkouts_for_checking:
        return []

    placeholders = ", ".join(["(%s, %s, %s, %s)"] * len(checkouts_for_checking))
    query = f"""
        SELECT
            git_repository_branch, git_repository_url, origin
        FROM
            notifications_checkout
        WHERE
            (git_repository_branch, git_repository_url, origin, path) IN ({placeholders})
            AND notification_sent >= datetime('now', '-{RESEND_INTERVAL}')
        """
    with connections["notifications"].cursor() as cursor:
        cursor.execute(
            query, [item for checkout in checkouts_for_checking for item in checkout]
        )
        sent_reports = cursor.fetchall()

    return sent_reports
