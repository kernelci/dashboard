from kernelCI_cache.utils import get_current_timestamp_kcidb_format
from kernelCI_cache.models import NotificationsCheckout


def mark_checkout_notification_as_sent(
    *,
    checkout_id: str,
    msg_id: str,
) -> bool:
    try:
        timestamp = get_current_timestamp_kcidb_format()
        NotificationsCheckout.objects.using("cache").create(
            checkout_id=checkout_id, notification_id=msg_id, notification_sent=timestamp
        )
        return True
    except Exception as e:
        print(f"Error storing notification checkout: {e}")
        return False
