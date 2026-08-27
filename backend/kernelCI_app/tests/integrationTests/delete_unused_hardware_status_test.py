"""Integration tests for delete_unused_hardware_status retention.

Pins the #1983 regression: hardware_status rows for non-tip checkouts inside the
retention window must survive the weekly cron.
"""

from io import StringIO

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from kernelCI_app.models import HardwareStatus, LatestCheckout
from kernelCI_app.tests.factories import CheckoutFactory

RETENTION_DAYS = 7


def _days_ago(days: int):
    return timezone.now() - timezone.timedelta(days=days)


def _run_delete(**kwargs) -> str:
    out = StringIO()
    err = StringIO()
    call_command("delete_unused_hardware_status", stdout=out, stderr=err, **kwargs)
    return out.getvalue() + err.getvalue()


def _make_hardware_status(
    *, checkout, platform: str, start_time, test_origin="maestro"
):
    return HardwareStatus.objects.create(
        checkout_id=checkout.id,
        test_origin=test_origin,
        platform=platform,
        compatibles=None,
        start_time=start_time,
        test_pass=1,
    )


@pytest.mark.django_db
@override_settings(HARDWARE_STATUS_RETENTION_DAYS=RETENTION_DAYS)
def test_keeps_non_tip_hardware_within_window():
    """#1983: board tested on an older (non-tip) checkout must not be wiped.

    Tip checkout is in latest_checkout and has no board. Older checkout is not a
    tip but is inside the retention window and has the board. Old tip-based cron
    deleted that row; time-window retention must keep it.
    """
    tip = CheckoutFactory(start_time=_days_ago(1), id="ret_tip_checkout")
    older = CheckoutFactory(start_time=_days_ago(3), id="ret_older_checkout")

    LatestCheckout.objects.create(
        checkout_id=tip.id,
        start_time=tip.start_time,
        origin=tip.origin,
        tree_name=tip.tree_name,
        git_repository_url=tip.git_repository_url,
        git_repository_branch=tip.git_repository_branch,
    )

    board = _make_hardware_status(
        checkout=older, platform="exynos", start_time=older.start_time
    )

    _run_delete()

    assert HardwareStatus.objects.filter(
        test_origin=board.test_origin,
        platform=board.platform,
        checkout_id=board.checkout_id,
    ).exists()


@pytest.mark.django_db
@override_settings(HARDWARE_STATUS_RETENTION_DAYS=RETENTION_DAYS)
def test_deletes_hardware_older_than_retention():
    old = CheckoutFactory(start_time=_days_ago(RETENTION_DAYS + 5), id="ret_old_hw")
    board = _make_hardware_status(
        checkout=old, platform="old-board", start_time=old.start_time
    )

    _run_delete()

    assert not HardwareStatus.objects.filter(
        test_origin=board.test_origin,
        platform=board.platform,
        checkout_id=board.checkout_id,
    ).exists()


@pytest.mark.django_db
@override_settings(HARDWARE_STATUS_RETENTION_DAYS=RETENTION_DAYS)
def test_does_not_wipe_recent_sibling_platform_rows():
    """Deleting by checkout_id alone would wipe in-window siblings. Must not."""
    checkout = CheckoutFactory(start_time=_days_ago(2), id="ret_sibling_checkout")
    stale = _make_hardware_status(
        checkout=checkout,
        platform="stale-board",
        start_time=_days_ago(RETENTION_DAYS + 5),
    )
    fresh = _make_hardware_status(
        checkout=checkout,
        platform="fresh-board",
        start_time=checkout.start_time,
    )

    _run_delete()

    assert not HardwareStatus.objects.filter(
        test_origin=stale.test_origin,
        platform=stale.platform,
        checkout_id=stale.checkout_id,
    ).exists()
    assert HardwareStatus.objects.filter(
        test_origin=fresh.test_origin,
        platform=fresh.platform,
        checkout_id=fresh.checkout_id,
    ).exists()


@pytest.mark.django_db
@override_settings(HARDWARE_STATUS_RETENTION_DAYS=RETENTION_DAYS)
def test_dry_run_deletes_nothing():
    old = CheckoutFactory(start_time=_days_ago(RETENTION_DAYS + 5), id="ret_dry_run")
    board = _make_hardware_status(
        checkout=old, platform="dry-board", start_time=old.start_time
    )

    output = _run_delete(dry_run=True)

    assert "DRY RUN" in output
    assert HardwareStatus.objects.filter(
        test_origin=board.test_origin,
        platform=board.platform,
        checkout_id=board.checkout_id,
    ).exists()
