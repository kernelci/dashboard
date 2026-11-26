from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import requests
from kernelCI_app.helpers.regzbot import (
    confirm_pending_regzbot_messages,
    regzbot_tracking_url,
    regzbot_url_for_issue,
)

NOW = datetime(2026, 11, 26, 15, 0, tzinfo=timezone.utc)


def _row(issue_id, message_id, *, confirmed_at=None):
    return SimpleNamespace(
        issue_id=issue_id,
        message_id=message_id,
        confirmed_at=confirmed_at,
        save=MagicMock(),
    )


@patch("kernelCI_app.helpers.regzbot.RegzbotMessage.objects")
def test_url_stays_hidden_until_the_page_is_confirmed(mock_objects):
    mock_objects.filter.return_value.first.return_value = _row(
        "issue-1", "pending@kernelci.org"
    )

    assert regzbot_url_for_issue("issue-1") is None


@patch("kernelCI_app.helpers.regzbot.RegzbotMessage.objects")
def test_url_is_returned_after_confirmation(mock_objects):
    mock_objects.filter.return_value.first.return_value = _row(
        "issue-1",
        "<published@kernelci.org>",
        confirmed_at=NOW,
    )

    assert regzbot_url_for_issue("issue-1") == regzbot_tracking_url(
        "published@kernelci.org"
    )


@patch("kernelCI_app.helpers.regzbot.http.head")
@patch("kernelCI_app.helpers.regzbot.RegzbotMessage.objects")
def test_only_http_200_confirms_a_pending_message(mock_objects, mock_head):
    timed_out = _row("issue-timeout", "timeout@kernelci.org")
    published = _row("issue-published", "published@kernelci.org")
    missing = _row("issue-missing", "missing@kernelci.org")
    mock_objects.filter.return_value = [timed_out, published, missing]

    def head(url, **kwargs):
        if "timeout@" in url:
            raise requests.Timeout("timed out")
        response = MagicMock()
        response.status_code = 200 if "published@" in url else 404
        return response

    mock_head.side_effect = head

    confirmed, pending = confirm_pending_regzbot_messages()

    assert (confirmed, pending) == (1, 2)
    assert published.confirmed_at is not None
    published.save.assert_called_once_with(update_fields=["confirmed_at"])
    assert missing.confirmed_at is None
    missing.save.assert_not_called()
    timed_out.save.assert_not_called()
