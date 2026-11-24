import json
from datetime import timedelta

import pytest
from django.utils import timezone

from kernelCI_app.management.commands.notifications import discard_sent_reports
from kernelCI_cache.models import NotificationsCheckout
from kernelCI_cache.queries.notifications import mark_checkout_notification_as_sent

pytestmark = pytest.mark.django_db(databases=["default", "notifications"])

TREE = ("master", "https://example.org/linux.git", "maestro")
REPORT = {"branch": TREE[0], "giturl": TREE[1]}


@pytest.mark.parametrize("path", ["%", ["boot%", "ltp%"]])
def test_sent_summary_keeps_unsent_sibling_until_resend_interval_expires(path):
    sent = REPORT if path == "%" else {**REPORT, "path": path}
    sibling = {**REPORT, "path": ["rt-tests%"]}
    reports = {TREE: [sent, sibling]}

    assert mark_checkout_notification_as_sent(
        msg_id="summary",
        checkout_id="checkout",
        git_repository_branch=TREE[0],
        git_repository_url=TREE[1],
        origin=TREE[2],
        path=path,
    )
    row = NotificationsCheckout.objects.using("notifications").get()
    assert row.notification_message_id == "summary"
    assert row.path == ("%" if path == "%" else json.dumps(path))

    assert discard_sent_reports({TREE}, reports, skip_sent_reports=False) == (
        {TREE},
        {TREE: [sibling]},
    )

    row.notification_sent = timezone.now() - timedelta(hours=13)
    row.save(using="notifications", update_fields=["notification_sent"])
    assert discard_sent_reports({TREE}, reports, skip_sent_reports=False) == (
        {TREE},
        {TREE: [sent, sibling]},
    )


@pytest.mark.parametrize("stored_path", ["['boot%', 'ltp%']", '["boot%", "ltp%"]'])
def test_recent_summary_recognizes_existing_path_formats(stored_path):
    NotificationsCheckout.objects.using("notifications").create(
        notification_message_id="previous-summary",
        notification_sent=timezone.now(),
        checkout_id="checkout",
        git_repository_branch=TREE[0],
        git_repository_url=TREE[1],
        origin=TREE[2],
        path=stored_path,
    )
    reports = {TREE: [{**REPORT, "path": ["boot%", "ltp%"]}]}
    assert discard_sent_reports({TREE}, reports, skip_sent_reports=False) == (set(), {})
