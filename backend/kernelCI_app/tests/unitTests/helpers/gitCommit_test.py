import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from django.test import override_settings

from kernelCI_app.helpers.gitCommit import (
    MAX_EPHEMERAL_PACK_BYTES,
    CommitParseError,
    FetchFailedError,
    InvalidGitUrlError,
    MissingGitUrlError,
    OversizedPackError,
    UnexpectedFetchObjectsError,
    assert_single_commit_fetch,
    fetch_commit_metadata,
    parse_commit,
    parse_commit_object,
    resolve_checkout_git_url,
    sanitize_git_url,
)
from kernelCI_app.tests.unitTests.helpers.fixtures.git_commit_data import (
    FIRST_PARENT,
    MERGE_COMMIT_HASH,
    MERGE_COMMIT_OBJECT,
    SECOND_PARENT,
)


def _run_git(repo: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Alice Author",
        "GIT_AUTHOR_EMAIL": "alice@example.com",
        "GIT_COMMITTER_NAME": "Bob Committer",
        "GIT_COMMITTER_EMAIL": "bob@example.com",
        "GIT_AUTHOR_DATE": "2001-09-09T01:46:40+0000",
        "GIT_COMMITTER_DATE": "2001-09-09T01:47:40-0500",
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


def _build_repo_with_merge(tmp_path: Path) -> tuple[Path, str, str, str]:
    repo = tmp_path / "src"
    repo.mkdir()
    _run_git(repo, "init", "-b", "main")
    _run_git(repo, "config", "user.name", "Alice Author")
    _run_git(repo, "config", "user.email", "alice@example.com")
    _run_git(repo, "config", "uploadpack.allowFilter", "true")
    _run_git(repo, "config", "uploadpack.allowAnySHA1InWant", "true")
    (repo / "a.txt").write_text("a\n")
    _run_git(repo, "add", "a.txt")
    _run_git(repo, "commit", "-m", "root commit")
    root = _run_git(repo, "rev-parse", "HEAD")

    _run_git(repo, "checkout", "-b", "other")
    (repo / "b.txt").write_text("b\n")
    _run_git(repo, "add", "b.txt")
    _run_git(repo, "commit", "-m", "side commit")
    side = _run_git(repo, "rev-parse", "HEAD")

    _run_git(repo, "checkout", "main")
    _run_git(repo, "merge", "--no-ff", "-m", "merge side\n\nmerge body\n", "other")
    merge = _run_git(repo, "rev-parse", "HEAD")
    return repo, root, side, merge


class TestParseCommitObject:
    def test_author_committer_subject_ordered_parents(self):
        metadata = parse_commit_object(
            raw=MERGE_COMMIT_OBJECT, git_commit_hash=MERGE_COMMIT_HASH
        )

        assert metadata.git_commit_hash == MERGE_COMMIT_HASH
        assert metadata.author_name == "Alice Author"
        assert metadata.author_email == "alice@example.com"
        assert metadata.author_date == datetime(
            2001, 9, 9, 1, 46, 40, tzinfo=timezone.utc
        )
        assert metadata.committer_name == "Bob Committer"
        assert metadata.committer_email == "bob@example.com"
        assert metadata.committer_date == datetime(
            2001, 9, 8, 20, 47, 40, tzinfo=timezone(timedelta(hours=-5))
        )
        assert metadata.subject == "Add feature foo"
        assert metadata.message.startswith("Add feature foo\n")
        assert "Longer body" in metadata.message
        assert metadata.parent_hashes == (FIRST_PARENT, SECOND_PARENT)

    def test_missing_separator_raises(self):
        with pytest.raises(CommitParseError):
            parse_commit_object(raw="tree abc\n", git_commit_hash=MERGE_COMMIT_HASH)


class TestParseCommitFromRepo:
    def test_parse_existing_repo_does_not_fetch(self, tmp_path, monkeypatch):
        repo, root, side, merge = _build_repo_with_merge(tmp_path)
        calls: list[list[str]] = []
        real_run = subprocess.run

        def wrapped(*args, **kwargs):
            command = args[0] if args else kwargs.get("args")
            if isinstance(command, list):
                calls.append(command)
            return real_run(*args, **kwargs)

        monkeypatch.setattr("kernelCI_app.helpers.gitCommit.subprocess.run", wrapped)

        metadata = parse_commit(repo_path=str(repo), git_commit_hash=merge)

        assert metadata.git_commit_hash == merge
        assert metadata.parent_hashes == (root, side)
        assert metadata.subject == "merge side"
        assert metadata.message.startswith("merge side\n")
        assert all("fetch" not in command for command in calls)


class TestSanitizeGitUrl:
    def test_accepts_https_and_file(self):
        https = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/"
        assert (
            sanitize_git_url(https)
            == "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
        )
        assert sanitize_git_url("file:///tmp/linux.git") == "file:///tmp/linux.git"

    def test_malformed_does_not_raise(self):
        for url in (
            "",
            "   ",
            None,
            "https://example.com/",
            "https://example.com",
            "linux.git",
            "git@github.com:org/repo.git",
            "not a url at all!!!",
        ):
            assert sanitize_git_url(url) is None


class TestResolveCheckoutGitUrl:
    @patch("kernelCI_app.helpers.gitCommit.Checkouts.objects")
    def test_prefers_maestro_kernel_org(self, mock_objects):
        rows = mock_objects.filter.return_value.values_list.return_value
        rows.distinct.return_value = [
            ("redhat", "https://github.com/foo/linux.git"),
            (
                "maestro",
                "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
            ),
            ("maestro", "https://github.com/torvalds/linux.git"),
        ]
        assert resolve_checkout_git_url("abc") == (
            "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
        )

    @patch("kernelCI_app.helpers.gitCommit.Checkouts.objects")
    def test_skips_malformed_urls(self, mock_objects):
        rows = mock_objects.filter.return_value.values_list.return_value
        rows.distinct.return_value = [
            ("maestro", "git@github.com:org/repo.git"),
            ("maestro", "https://example.com/"),
            (
                "redhat",
                "https://git.kernel.org/pub/scm/linux/kernel/git/redhat/linux.git",
            ),
        ]
        assert resolve_checkout_git_url("abc") == (
            "https://git.kernel.org/pub/scm/linux/kernel/git/redhat/linux.git"
        )


class TestFetchCommitMetadata:
    def test_fetch_from_local_repo_then_wipes(self, tmp_path):
        repo, _root, _side, merge = _build_repo_with_merge(tmp_path)
        scratch = tmp_path / "scratch"
        with override_settings(GIT_SCRATCH_DIR=str(scratch)):
            metadata = fetch_commit_metadata(merge, url=f"file://{repo}")

        assert metadata.git_commit_hash == merge
        assert metadata.subject == "merge side"
        assert metadata.parent_hashes[0] == _root
        leftover = list(scratch.glob("commit-fetch-*"))
        assert leftover == []

    def test_fetch_failure(self, tmp_path):
        scratch = tmp_path / "scratch"
        with override_settings(GIT_SCRATCH_DIR=str(scratch)):
            with pytest.raises(FetchFailedError):
                fetch_commit_metadata("a" * 40, url="file:///no/such/repo.git")
        leftover = list(scratch.glob("commit-fetch-*"))
        assert leftover == []

    def test_bad_url(self):
        with pytest.raises(InvalidGitUrlError):
            fetch_commit_metadata("a" * 40, url="git@github.com:org/repo.git")

    @patch("kernelCI_app.helpers.gitCommit.resolve_checkout_git_url", return_value=None)
    def test_missing_url(self, _mock_resolve):
        with pytest.raises(MissingGitUrlError):
            fetch_commit_metadata("a" * 40)

    def test_oversized_pack(self, tmp_path):
        repo = tmp_path / "bare.git"
        (repo / "objects" / "pack").mkdir(parents=True)
        pack = repo / "objects" / "pack" / "pack-deadbeef.pack"
        pack.write_bytes(b"\0" * (MAX_EPHEMERAL_PACK_BYTES + 1))
        with pytest.raises(OversizedPackError):
            assert_single_commit_fetch(repo)

    def test_full_pack_extra_commits(self, tmp_path, monkeypatch):
        repo = tmp_path / "bare.git"
        repo.mkdir()
        monkeypatch.setattr(
            "kernelCI_app.helpers.gitCommit._object_type_counts",
            lambda _repo: {"commit": 12},
        )
        monkeypatch.setattr(
            "kernelCI_app.helpers.gitCommit._pack_bytes", lambda _repo: 10
        )
        with pytest.raises(UnexpectedFetchObjectsError):
            assert_single_commit_fetch(repo)

    def test_full_pack_includes_trees(self, tmp_path, monkeypatch):
        repo = tmp_path / "bare.git"
        repo.mkdir()
        monkeypatch.setattr(
            "kernelCI_app.helpers.gitCommit._object_type_counts",
            lambda _repo: {"commit": 1, "tree": 4, "blob": 20},
        )
        monkeypatch.setattr(
            "kernelCI_app.helpers.gitCommit._pack_bytes", lambda _repo: 10
        )
        with pytest.raises(UnexpectedFetchObjectsError):
            assert_single_commit_fetch(repo)
