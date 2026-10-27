from types import SimpleNamespace

import pytest

from kernelCI_app.management.commands.update_db import Command


@pytest.mark.parametrize("method", ["restore_commits", "restore_commit_parents"])
def test_restore_skips_commit_files_missing_from_legacy_snapshot(method):
    command = Command()
    command.snapshot_archive = SimpleNamespace(getnames=lambda: [])

    getattr(command, method)()


@pytest.mark.parametrize(
    "record",
    [
        (1, "a" * 40, 2, "", 3, ""),
        (1, "a" * 40, 2, "", 3, "", "https://old.example/repo"),
        (
            1,
            "a" * 40,
            "Author",
            "a@example.com",
            "",
            "Committer",
            "c@example.com",
            "",
            "Subject",
            "Message",
            "https://old.example/repo",
        ),
    ],
)
def test_restore_commits_accepts_current_and_legacy_snapshot_rows(monkeypatch, record):
    command = Command()
    captured = []

    def bulk_create(rows, **kwargs):
        captured.extend(rows)
        return rows

    monkeypatch.setattr(
        "kernelCI_app.management.commands.update_db.Commits.objects.bulk_create",
        bulk_create,
    )
    monkeypatch.setattr(
        "kernelCI_app.management.commands.update_db.CommitMessage.objects.bulk_create",
        lambda rows, **kwargs: rows,
    )
    monkeypatch.setattr(command, "_identity_id", lambda *args: 2)
    monkeypatch.setattr(command, "sync_id_sequence", lambda *args: None)

    assert command.insert_commits_data([record]) == 1
    assert captured[0].git_commit_hash == "a" * 40
    assert not hasattr(captured[0], "fetched_from_url")
