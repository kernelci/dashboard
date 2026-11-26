from django.utils import timezone

import requests
from kernelCI_app.helpers import http
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.models import RegzbotMessage


def _bare_message_id(message_id: str) -> str:
    return message_id.strip().strip("<>")


def regzbot_tracking_url(message_id: str) -> str:
    return (
        "https://linux-regtracking.leemhuis.info/regzbot/regression/lore/"
        f"{_bare_message_id(message_id)}/"
    )


def record_regzbot_message(*, issue_id: str, message_id: str) -> None:
    RegzbotMessage.objects.get_or_create(
        issue_id=issue_id,
        defaults={"message_id": _bare_message_id(message_id)},
    )


def regzbot_url_for_issue(issue_id: str) -> str | None:
    row = RegzbotMessage.objects.filter(pk=issue_id).first()
    if row is None or row.confirmed_at is None:
        return None
    return regzbot_tracking_url(row.message_id)


def confirm_pending_regzbot_messages() -> tuple[int, int]:
    now = timezone.now()
    confirmed = 0
    pending = 0
    for row in RegzbotMessage.objects.filter(confirmed_at__isnull=True):
        try:
            response = http.head(regzbot_tracking_url(row.message_id), timeout=10)
        except requests.RequestException as exc:
            log_message(f"Regzbot probe failed for {row.issue_id}: {exc}")
            pending += 1
            continue
        if response.status_code == 200:
            row.confirmed_at = now
            row.save(update_fields=["confirmed_at"])
            confirmed += 1
            continue
        if response.status_code != 404:
            log_message(
                f"Regzbot probe for {row.issue_id} returned {response.status_code}"
            )
        pending += 1
    return confirmed, pending
