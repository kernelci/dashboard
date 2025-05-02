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
        NotificationsCheckout.objects.using("cache").create(
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
) -> bool:
    """Creates an entry for an issue notification"""
    try:
        timestamp = get_current_timestamp_kcidb_format()
        NotificationsIssue.objects.using("cache").create(
            notification_message_id=msg_id,
            notification_sent=timestamp,
            issue_id=issue_id,
            issue_version=issue_version,
        )
        return True
    except Exception as e:
        log_message(f"Error marking issue notification_sent:\n{e}")
        return False
