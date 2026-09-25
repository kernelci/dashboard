import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
from django.core.management import call_command
from django.test import override_settings

from kernelCI_app.helpers import commitSync
from kernelCI_app.helpers.commitSync import (
    TIPS_FILENAME,
    _parse_batch_output,
    allowlisted_tree_urls,
    ensure_mirror,
    fetch_remote,
    insert_commits,
    list_tips,
    new_commit_hashes,
    parse_commits,
    sync_commit_metadata,
)
from kernelCI_app.helpers.gitCommit import CommitMetadata


def _run_git(repo: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Alice Author",
        "GIT_AUTHOR_EMAIL": "alice@example.com",
        "GIT_COMMITTER_NAME": "Bob Committer",
        "GIT_COMMITTER_EMAIL": "bob@example.com",
        "GIT_AUTHOR_DATE": "2001-09-09T01:46:40+0000",
        "GIT_COMMITTER_DATE": "2001-09-09T01:47:40+0000",
    }
    git = shutil.which("git")
    assert git is not None
    result = subprocess.run(  # noqa: S603
        [git, "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def _linear_repo(tmp_path: Path) -> tuple[Path, list[str]]:
    repo = tmp_path / "src"
    repo.mkdir()
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "config", "user.name", "Alice Author")
    _run_git(repo, "config", "user.email", "alice@example.com")
    _run_git(repo, "config", "uploadpack.allowFilter", "true")
    hashes: list[str] = []
    for name in ("root", "skipped", "tip"):
        (repo / "f.txt").write_text(name + "\n")
        _run_git(repo, "add", "f.txt")
        _run_git(repo, "commit", "-m", name)
        hashes.append(_run_git(repo, "rev-parse", "HEAD"))
    return repo, hashes


def _metadata(
    git_commit_hash: str,
    *parents: str,
    subject: str = "subj",
) -> CommitMetadata:
    now = datetime(2001, 9, 9, 1, 46, 40, tzinfo=timezone.utc)
    return CommitMetadata(
        git_commit_hash=git_commit_hash,
        author_name="Alice Author",
        author_email="alice@example.com",
        author_date=now,
        committer_name="Bob Committer",
        committer_email="bob@example.com",
        committer_date=now,
        subject=subject,
        message=subject + "\n",
        parent_hashes=parents,
    )


@pytest.fixture
def commit_store(monkeypatch):
    commits_by_hash: dict[str, object] = {}
    parent_rows: list[object] = []
    next_id = {"n": 1}

    class _Filter:
        def __init__(self, hashes: set[str]):
            self.hashes = hashes

        def values_list(self, *_args):
            return [
                (git_hash, obj.id)
                for git_hash, obj in commits_by_hash.items()
                if git_hash in self.hashes
            ]

    class _Commits:
        def bulk_create(self, rows, **_kwargs):
            for row in rows:
                if row.git_commit_hash in commits_by_hash:
                    continue
                row.id = next_id["n"]
                next_id["n"] += 1
                commits_by_hash[row.git_commit_hash] = row
            return rows

        def filter(self, git_commit_hash__in=None):
            return _Filter(set(git_commit_hash__in or []))

        def values(self, *_args):
            return [{"git_commit_hash": git_hash} for git_hash in commits_by_hash]

    class _Parents:
        def bulk_create(self, rows, **_kwargs):
            parent_rows.extend(rows)
            return rows

    monkeypatch.setattr("kernelCI_app.helpers.commitSync.Commits.objects", _Commits())
    monkeypatch.setattr(
        "kernelCI_app.helpers.commitSync.CommitParents.objects", _Parents()
    )
    return commits_by_hash, parent_rows


_TREES_FILE = {
    "trees": {
        "bad": {"url": "git@github.com:org/repo.git"},
        "mainline": {
            "url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/"
        },
        "dup": {
            "url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
        },
    }
}
_MAINLINE_URL = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"


class TestAllowlistedTreeUrls:
    def test_skips_malformed_and_dedupes(self, monkeypatch):
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.TreeproofCommand.generate_tree_names",
            lambda _self: _TREES_FILE,
        )
        assert allowlisted_tree_urls() == [_MAINLINE_URL]

    def test_without_refresh_reads_file_only(self, monkeypatch):
        def fail(_self):
            raise AssertionError("should not regenerate the tree names file")

        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.TreeproofCommand.generate_tree_names", fail
        )
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.get_tree_file_data",
            lambda: _TREES_FILE,
        )
        assert allowlisted_tree_urls(refresh=False) == [_MAINLINE_URL]


class TestParseBatchOutput:
    def test_reads_records_and_skips_missing(self):
        good = b"tree abc\nauthor A <a@e.com> 1000000000 +0000\n\nsubject line\n"
        raw = (
            b"%s commit %d\n%s\n" % (b"aa" * 20, len(good), good)
            + b"%s missing\n" % (b"bb" * 20)
            + b"%s commit %d\n%s\n" % (b"cc" * 20, len(good), good)
        )

        parsed = _parse_batch_output(raw)

        assert [item.git_commit_hash for item in parsed] == ["aa" * 20, "cc" * 20]
        assert parsed[0].subject == "subject line"

    def test_payload_with_newlines_does_not_desync_records(self):
        body = b"tree abc\nauthor A <a@e.com> 1000000000 +0000\n\nfirst\n\nsecond\n"
        raw = b"%s commit %d\n%s\n%s commit %d\n%s\n" % (
            b"aa" * 20,
            len(body),
            body,
            b"cc" * 20,
            len(body),
            body,
        )

        parsed = _parse_batch_output(raw)

        assert len(parsed) == 2
        assert parsed[1].git_commit_hash == "cc" * 20
        assert parsed[1].message == "first\n\nsecond\n"


class TestUpsertCommits:
    def test_topo_order_first_parent_edges(self, commit_store):
        commits_by_hash, parent_rows = commit_store
        root = _metadata("aa" * 20, subject="root")
        skipped = _metadata("bb" * 20, "aa" * 20, subject="skipped")
        tip = _metadata("cc" * 20, "bb" * 20, subject="tip")

        commit_count, edge_count = insert_commits([root, skipped, tip])

        assert commit_count == 3
        assert edge_count == 2
        assert set(commits_by_hash) == {"aa" * 20, "bb" * 20, "cc" * 20}
        ords = {(row.commit_id, row.parent_id, row.ord) for row in parent_rows}
        assert ords == {
            (commits_by_hash["bb" * 20].id, commits_by_hash["aa" * 20].id, 0),
            (commits_by_hash["cc" * 20].id, commits_by_hash["bb" * 20].id, 0),
        }

    def test_skips_edge_when_parent_row_missing(self, commit_store):
        _commits_by_hash, parent_rows = commit_store
        child = _metadata("dd" * 20, "ee" * 20, subject="orphan-parent")

        commit_count, edge_count = insert_commits([child])

        assert commit_count == 1
        assert edge_count == 0
        assert parent_rows == []


class TestSyncCommitMetadata:
    def test_skipped_intermediate_commit_is_ingested(
        self, tmp_path, monkeypatch, commit_store
    ):
        repo, hashes = _linear_repo(tmp_path)
        root, skipped, tip = hashes
        mirror = tmp_path / "mirror"
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.allowlisted_tree_urls",
            lambda **_kwargs: [f"file://{repo}"],
        )
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.checkout_branches_by_url",
            lambda: {},
        )

        stats = sync_commit_metadata(mirror_dir=mirror)
        commits_by_hash, parent_rows = commit_store

        assert stats["remotes_ok"] == 1
        assert stats["remotes_failed"] == 0
        assert stats["commits_written"] == 3
        assert skipped in commits_by_hash
        assert set(commits_by_hash) == {root, skipped, tip}
        first_parents = {
            (row.commit_id, row.parent_id, row.ord)
            for row in parent_rows
            if row.ord == 0
        }
        assert (
            commits_by_hash[skipped].id,
            commits_by_hash[root].id,
            0,
        ) in first_parents
        assert (
            commits_by_hash[tip].id,
            commits_by_hash[skipped].id,
            0,
        ) in first_parents

    def test_one_remote_fails_others_still_write(
        self, tmp_path, monkeypatch, commit_store
    ):
        repo, hashes = _linear_repo(tmp_path)
        mirror = tmp_path / "mirror"
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.allowlisted_tree_urls",
            lambda **_kwargs: ["file:///no/such/repo.git", f"file://{repo}"],
        )
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.checkout_branches_by_url",
            lambda: {},
        )

        stats = sync_commit_metadata(mirror_dir=mirror)

        assert stats["remotes_failed"] == 1
        assert stats["remotes_ok"] == 1
        assert stats["commits_written"] == 3
        assert set(commit_store[0]) == set(hashes)

    def test_dry_run_writes_nothing(self, tmp_path, monkeypatch, commit_store):
        repo, _hashes = _linear_repo(tmp_path)
        mirror = tmp_path / "mirror"
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.allowlisted_tree_urls",
            lambda **_kwargs: [f"file://{repo}"],
        )
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.checkout_branches_by_url",
            lambda: {},
        )

        stats = sync_commit_metadata(mirror_dir=mirror, dry_run=True)

        assert stats["parsed"] == 3
        assert stats["commits_written"] == 0
        assert commit_store[0] == {}
        assert commit_store[1] == []
        assert not (mirror / TIPS_FILENAME).exists()

    def test_fetch_only_then_ingest_matches_combined(
        self, tmp_path, monkeypatch, commit_store
    ):
        repo, hashes = _linear_repo(tmp_path)
        mirror = tmp_path / "mirror"
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.allowlisted_tree_urls",
            lambda **_kwargs: [f"file://{repo}"],
        )
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.checkout_branches_by_url",
            lambda: {},
        )

        fetch_stats = sync_commit_metadata(mirror_dir=mirror, skip_ingest=True)
        assert fetch_stats["remotes_ok"] == 1
        assert fetch_stats["commits_written"] == 0
        assert commit_store[0] == {}
        assert not (mirror / TIPS_FILENAME).exists()

        ingest_stats = sync_commit_metadata(mirror_dir=mirror, skip_fetch=True)
        assert ingest_stats["commits_written"] == 3
        assert set(commit_store[0]) == set(hashes)
        assert (mirror / TIPS_FILENAME).is_file()

        again = sync_commit_metadata(mirror_dir=mirror, skip_fetch=True)
        assert again["parsed"] == 0
        assert again["commits_written"] == 0

    def test_skip_fetch_and_skip_ingest_is_invalid(self, tmp_path):
        with pytest.raises(ValueError, match="cannot both be set"):
            sync_commit_metadata(
                mirror_dir=tmp_path / "mirror",
                skip_fetch=True,
                skip_ingest=True,
            )

    def test_enumerate_includes_skipped_without_db(self, tmp_path):
        repo, hashes = _linear_repo(tmp_path)
        mirror = tmp_path / "mirror"
        ensure_mirror(mirror)
        assert fetch_remote(mirror, url=f"file://{repo}", timeout=30)
        enumerated = new_commit_hashes(mirror, ())
        parsed = parse_commits(mirror, enumerated)
        assert [item.git_commit_hash for item in parsed] == hashes
        assert new_commit_hashes(mirror, list_tips(mirror)) == []

    def test_fill_gaps_uses_one_shot_fetch(self, tmp_path, monkeypatch, commit_store):
        gap_hash = "ff" * 20
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.allowlisted_tree_urls",
            lambda **_kwargs: [],
        )
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.missing_checkout_hashes",
            lambda: [gap_hash],
        )
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.fetch_commit_metadata",
            lambda git_commit_hash: _metadata(git_commit_hash, subject="gap"),
        )

        stats = sync_commit_metadata(
            mirror_dir=tmp_path / "mirror",
            skip_fetch=True,
            fill_gaps=True,
        )

        assert stats["gaps_fetched"] == 1
        assert stats["gaps_written"] == 1
        assert gap_hash in commit_store[0]


class TestFetchGuards:
    def test_does_not_fetch_unlisted_topic_branch(self, tmp_path, monkeypatch):
        repo, hashes = _linear_repo(tmp_path)
        _run_git(repo, "checkout", "-b", "topic")
        (repo / "f.txt").write_text("topic\n")
        _run_git(repo, "add", "f.txt")
        _run_git(repo, "commit", "-m", "topic only")
        topic = _run_git(repo, "rev-parse", "HEAD")
        _run_git(repo, "checkout", "main")

        mirror = tmp_path / "mirror"
        ensure_mirror(mirror)
        assert fetch_remote(
            mirror,
            url=f"file://{repo}",
            timeout=30,
            branches={"main"},
        )
        enumerated = new_commit_hashes(mirror, ())
        assert topic not in enumerated
        assert set(enumerated) == set(hashes)

    def test_oversized_pack_is_rolled_back(self, tmp_path, monkeypatch):
        repo, _hashes = _linear_repo(tmp_path)
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.MAX_REMOTE_PACK_BYTES",
            1,
        )
        mirror = tmp_path / "mirror"
        ensure_mirror(mirror)
        assert (
            fetch_remote(mirror, url=f"file://{repo}", timeout=30, branches=set())
            is False
        )
        pack_dir = mirror / "objects" / "pack"
        packs = list(pack_dir.glob("*.pack")) if pack_dir.is_dir() else []
        assert packs == []
        assert new_commit_hashes(mirror, ()) == []

    def test_rejected_pack_is_not_downloaded_twice(self, tmp_path, monkeypatch):
        repo, _hashes = _linear_repo(tmp_path)
        monkeypatch.setattr(
            "kernelCI_app.helpers.commitSync.MAX_REMOTE_PACK_BYTES",
            1,
        )
        attempts: list[list[str]] = []
        real_fetch = commitSync._fetch_refspecs_or_rollback

        def counting_fetch(repo_dir, *, refspecs, **kwargs):
            attempts.append(refspecs)
            return real_fetch(repo_dir, refspecs=refspecs, **kwargs)

        monkeypatch.setattr(commitSync, "_fetch_refspecs_or_rollback", counting_fetch)
        mirror = tmp_path / "mirror"
        ensure_mirror(mirror)

        assert (
            fetch_remote(mirror, url=f"file://{repo}", timeout=30, branches={"main"})
            is False
        )
        assert len(attempts) == 1

    def test_failed_fetch_retries_and_keeps_objects(self, tmp_path, monkeypatch):
        repo, hashes = _linear_repo(tmp_path)
        mirror = tmp_path / "mirror"
        ensure_mirror(mirror)
        real_fetch = commitSync._fetch_refspecs_or_rollback
        attempts: list[int] = []

        def fail_once(repo_dir, **kwargs):
            attempts.append(1)
            if len(attempts) == 1:
                # Let git write the pack, then report the transport dying after it.
                real_fetch(repo_dir, **kwargs)
                return commitSync.FetchOutcome.FAILED
            return real_fetch(repo_dir, **kwargs)

        monkeypatch.setattr(commitSync, "_fetch_refspecs_or_rollback", fail_once)

        assert fetch_remote(mirror, url=f"file://{repo}", timeout=30, branches={"main"})
        assert len(attempts) == 2
        assert set(new_commit_hashes(mirror, ())) == set(hashes)

    def test_failed_fetch_keeps_downloaded_pack(self, tmp_path, monkeypatch):
        repo, _hashes = _linear_repo(tmp_path)
        mirror = tmp_path / "mirror"
        ensure_mirror(mirror)
        real_fetch = commitSync._fetch_refspecs_or_rollback

        def always_fail(repo_dir, **kwargs):
            real_fetch(repo_dir, **kwargs)
            return commitSync.FetchOutcome.FAILED

        monkeypatch.setattr(commitSync, "_fetch_refspecs_or_rollback", always_fail)

        assert (
            fetch_remote(mirror, url=f"file://{repo}", timeout=30, branches={"main"})
            is False
        )
        # Objects stay so the next run resumes instead of paying for them again.
        assert list((mirror / "objects" / "pack").glob("*.pack"))

    def test_unfilterable_server_is_still_fetched(self, tmp_path, monkeypatch):
        repo, hashes = _linear_repo(tmp_path)
        monkeypatch.setattr(
            commitSync,
            "_probe_remote",
            lambda _repo_dir, _name: ({"main"}, False),
        )
        mirror = tmp_path / "mirror"
        ensure_mirror(mirror)

        assert fetch_remote(mirror, url=f"file://{repo}", timeout=30, branches={"main"})
        assert set(new_commit_hashes(mirror, ())) == set(hashes)

    def test_skip_unfilterable_opts_out(self, tmp_path, monkeypatch):
        repo, _hashes = _linear_repo(tmp_path)
        monkeypatch.setattr(
            commitSync,
            "_probe_remote",
            lambda _repo_dir, _name: ({"main"}, False),
        )

        def fail(*_args, **_kwargs):
            raise AssertionError("must not fetch when opted out")

        monkeypatch.setattr(commitSync, "_fetch_refspecs_or_rollback", fail)
        mirror = tmp_path / "mirror"
        ensure_mirror(mirror)

        assert (
            fetch_remote(
                mirror,
                url=f"file://{repo}",
                timeout=30,
                branches={"main"},
                skip_unfilterable=True,
            )
            is False
        )


class TestSyncCommitCommands:
    def test_mirror_command_skips_ingest(self, monkeypatch):
        seen: dict[str, object] = {}

        def fake_sync(**kwargs):
            seen.update(kwargs)
            return {
                "remotes_ok": 0,
                "remotes_failed": 0,
                "parsed": 0,
                "commits_written": 0,
                "edges_written": 0,
                "gaps_fetched": 0,
                "gaps_written": 0,
            }

        monkeypatch.setattr(
            "kernelCI_app.management.commands.sync_commit_mirror.sync_commit_metadata",
            fake_sync,
        )
        with override_settings(GIT_MIRROR_DIR="/tmp/mirror"):
            call_command("sync_commit_mirror", "--dry-run")
        assert seen["skip_ingest"] is True
        assert seen["dry_run"] is True
        assert "skip_fetch" not in seen or seen.get("skip_fetch") is False

    def test_ingest_command_skips_fetch(self, monkeypatch):
        seen: dict[str, object] = {}

        def fake_sync(**kwargs):
            seen.update(kwargs)
            return {
                "remotes_ok": 0,
                "remotes_failed": 0,
                "parsed": 0,
                "commits_written": 0,
                "edges_written": 0,
                "gaps_fetched": 0,
                "gaps_written": 0,
            }

        monkeypatch.setattr(
            "kernelCI_app.management.commands.sync_commit_ingest.sync_commit_metadata",
            fake_sync,
        )
        with override_settings(GIT_MIRROR_DIR="/tmp/mirror"):
            call_command("sync_commit_ingest", "--fill-gaps")
        assert seen["skip_fetch"] is True
        assert seen["fill_gaps"] is True
        assert "skip_ingest" not in seen or seen.get("skip_ingest") is False
