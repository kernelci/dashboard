from types import SimpleNamespace

import pytest

from kernelCI_app.management.commands.update_db import Command


@pytest.mark.parametrize("method", ["restore_commits", "restore_commit_parents"])
def test_restore_skips_commit_files_missing_from_legacy_snapshot(method):
    command = Command()
    command.snapshot_archive = SimpleNamespace(getnames=lambda: [])

    getattr(command, method)()
