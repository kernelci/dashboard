from unittest.mock import patch

import pytest
from django.core.management.base import CommandError

from kernelCI_app.management.commands.monitor_submissions import (
    Command,
    get_stall_grace_minutes,
)


@pytest.mark.parametrize("value", ["invalid", "", "1.5", "0", "-1"])
def test_invalid_stall_grace_fails_before_setup(monkeypatch, value):
    monkeypatch.setenv("INGESTER_STALL_GRACE_MINUTES", value)
    command = Command()
    with patch.object(command, "_setup_prometheus") as setup:
        with pytest.raises(CommandError, match="must be a positive integer"):
            command.handle(
                spool_dir="/unused", max_workers=1, interval=5, trees_file=None
            )
        setup.assert_not_called()


def test_stall_grace_default_and_override(monkeypatch):
    monkeypatch.delenv("INGESTER_STALL_GRACE_MINUTES", raising=False)
    assert get_stall_grace_minutes() == 60
    monkeypatch.setenv("INGESTER_STALL_GRACE_MINUTES", "15")
    assert get_stall_grace_minutes() == 15


@pytest.mark.parametrize("error", [PermissionError("denied"), OSError("I/O error")])
def test_retry_scan_errors_do_not_clear_tracking(tmp_path, error):
    tracked = {"old.json": 0.0}
    with patch("os.scandir", side_effect=error):
        with pytest.raises(CommandError, match="Could not scan retry directory"):
            Command()._check_retry_backlog(str(tmp_path), str(tmp_path), tracked, 60)
    assert tracked == {"old.json": 0.0}


@pytest.fixture
def retry_dirs(tmp_path):
    pending = tmp_path / "pending_retry"
    pending.mkdir()
    return tmp_path, pending


def check_backlog(spool, pending, tracked, now):
    with patch("time.monotonic", return_value=now):
        return Command()._check_retry_backlog(str(spool), str(pending), tracked, 1)


def test_new_failures_do_not_reset_old_retry_age(retry_dirs):
    spool, pending = retry_dirs
    (pending / "old.json").write_text("{}")
    tracked = {}
    assert check_backlog(spool, pending, tracked, 0) == 1
    (pending / "new.json").write_text("{}")
    assert check_backlog(spool, pending, tracked, 30) == 2
    with pytest.raises(CommandError, match="old.json"):
        check_backlog(spool, pending, tracked, 61)


def test_requeued_file_retains_age_even_when_pending_is_empty(retry_dirs):
    spool, pending = retry_dirs
    path = pending / "old.json"
    path.write_text("{}")
    tracked = {}
    check_backlog(spool, pending, tracked, 0)
    path.rename(spool / path.name)
    assert check_backlog(spool, pending, tracked, 30) == 0
    with pytest.raises(CommandError, match="old.json"):
        check_backlog(spool, pending, tracked, 61)


def test_shrinking_backlog_does_not_reset_remaining_file_age(retry_dirs):
    spool, pending = retry_dirs
    for name in ("old.json", "done.json"):
        (pending / name).write_text("{}")
    tracked = {}
    check_backlog(spool, pending, tracked, 0)
    (pending / "done.json").unlink()
    assert check_backlog(spool, pending, tracked, 30) == 1
    assert tracked == {"old.json": 0}
    with pytest.raises(CommandError, match="old.json"):
        check_backlog(spool, pending, tracked, 61)


def test_successful_retries_do_not_stall_when_count_is_constant(retry_dirs):
    spool, pending = retry_dirs
    (pending / "old.json").write_text("{}")
    (pending / "notes.txt").write_text("ignored")
    tracked = {}
    assert check_backlog(spool, pending, tracked, 0) == 1
    (pending / "old.json").unlink()
    (pending / "new.json").write_text("{}")
    assert check_backlog(spool, pending, tracked, 61) == 1
    assert tracked == {"new.json": 61}


def test_retry_stat_error_does_not_clear_tracking(retry_dirs):
    spool, pending = retry_dirs
    tracked = {"old.json": 0}
    with patch("os.stat", side_effect=PermissionError("denied")):
        with pytest.raises(CommandError, match="Could not inspect deferred file"):
            check_backlog(spool, pending, tracked, 30)
    assert tracked == {"old.json": 0}
