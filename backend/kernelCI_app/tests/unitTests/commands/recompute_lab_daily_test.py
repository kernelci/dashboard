from datetime import date, datetime, timezone

import pytest
from django.core.management.base import CommandError

from kernelCI_app.management.commands.recompute_lab_daily import Command


@pytest.fixture(autouse=True)
def _dev_instance(monkeypatch):
    monkeypatch.setattr(
        "kernelCI_app.management.commands.recompute_lab_daily.get_running_instance",
        lambda: None,
    )


def _run(days=1, day=None):
    cmd = Command()
    seen = []
    cmd._recompute_day = seen.append
    return seen, cmd.handle(days=days, day=day)


def test_days_window_ends_on_today(monkeypatch):
    monkeypatch.setattr(
        "kernelCI_app.management.commands.recompute_lab_daily.timezone.now",
        lambda: datetime(2026, 10, 14, 12, tzinfo=timezone.utc),
    )

    seen, _ = _run(days=3)

    assert seen == [date(2026, 10, 12), date(2026, 10, 13), date(2026, 10, 14)]


def test_single_day_replaces_the_window(monkeypatch):
    monkeypatch.setattr(
        "kernelCI_app.management.commands.recompute_lab_daily.timezone.now",
        lambda: datetime(2026, 10, 14, 12, tzinfo=timezone.utc),
    )

    seen, _ = _run(days=15, day=date(2026, 1, 2))

    assert seen == [date(2026, 1, 2)]


def test_days_must_be_positive():
    with pytest.raises(CommandError):
        _run(days=0)


def test_listing_cache_clears_only_after_a_rewrite(monkeypatch):
    monkeypatch.setattr(
        "kernelCI_app.management.commands.recompute_lab_daily.timezone.now",
        lambda: datetime(2026, 10, 14, 12, tzinfo=timezone.utc),
    )
    cleared = []
    monkeypatch.setattr(
        "kernelCI_app.management.commands.recompute_lab_daily.clear_cache",
        cleared.append,
    )
    cmd = Command()

    cmd._recompute_day = lambda day: False
    cmd.handle(days=1, day=None)
    assert cleared == []

    cmd._recompute_day = lambda day: True
    cmd.handle(days=1, day=None)
    assert cleared == ["labListing"]
