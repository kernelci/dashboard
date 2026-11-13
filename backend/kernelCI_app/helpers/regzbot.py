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
    return regzbot_tracking_url(row.message_id) if row else None
