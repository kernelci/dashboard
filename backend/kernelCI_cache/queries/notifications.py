from kernelCI_cache.typeModels.databases import PossibleIssueType
from kernelCI_cache.utils import get_current_timestamp_kcidb_format
from kernelCI_cache.models import NotificationsCheckout, NotificationsIssue
from kernelCI_app.helpers.logger import log_message


def mark_checkout_notification_as_sent(
    *,
    checkout_id: str,
    msg_id: str,
) -> bool:
    try:
        timestamp = get_current_timestamp_kcidb_format()
        NotificationsCheckout.objects.using("notifications").create(
            checkout_id=checkout_id,
            notification_message_id=msg_id,
            notification_sent=timestamp,
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
