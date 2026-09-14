"""Parse git commit metadata. Optional one-shot SHA fetch; no DB writes.

Used as a fallback for hashes the mirrored-tree sync job (#2109) cannot
cover. Parse against an existing repo path so that job can reuse this
instead of duplicating commit-format parsing.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings

from kernelCI_app.models import Checkouts

FETCH_TIMEOUT_SECONDS = 60
# One commit object is tiny; a full kernel history pack is hundreds of MB.
MAX_EPHEMERAL_PACK_BYTES = 2 * 1024 * 1024
_IDENT_RE = re.compile(r"^([^<]*?) <([^>]*)> (\d+) ([+-]\d{4})$")
_GIT_ENV = {
    "GIT_TERMINAL_PROMPT": "0",
    "GCM_INTERACTIVE": "never",
}


class CommitMetadataError(Exception):
    """Typed failure from parse or one-shot fetch. No metadata returned."""


class InvalidGitUrlError(CommitMetadataError):
    pass


class MissingGitUrlError(CommitMetadataError):
    pass


class FetchFailedError(CommitMetadataError):
    pass


class OversizedPackError(CommitMetadataError):
    pass


class UnexpectedFetchObjectsError(CommitMetadataError):
    pass


class CommitParseError(CommitMetadataError):
    pass


@dataclass(frozen=True)
class CommitMetadata:
    git_commit_hash: str
    author_name: str | None
    author_email: str | None
    author_date: datetime | None
    committer_name: str | None
    committer_email: str | None
    committer_date: datetime | None
    subject: str | None
    message: str | None
    parent_hashes: tuple[str, ...]


def sanitize_git_url(git_url: str | None) -> str | None:
    """Treeproof-style cleanup. Returns None for malformed URLs; never raises."""
    if not isinstance(git_url, str) or not git_url.strip():
        return None

    raw = git_url.strip().rstrip("/")
    if "://" not in raw:
        return None

    parsed = urlparse(raw)
    if not parsed.scheme:
        return None
    if parsed.scheme != "file" and not parsed.netloc:
        return None
    if not [segment for segment in parsed.path.split("/") if segment]:
        return None
    return raw


def resolve_checkout_git_url(git_commit_hash: str) -> str | None:
    """Pick a fetch URL from checkouts for this hash. Prefer maestro / git.kernel.org."""
    rows = (
        Checkouts.objects.filter(
            git_commit_hash=git_commit_hash,
            git_repository_url__isnull=False,
        )
        .values_list("origin", "git_repository_url")
        .distinct()
    )

    best_url: str | None = None
    best_rank: tuple[int, str] | None = None
    for origin, url in rows:
        cleaned = sanitize_git_url(url)
        if cleaned is None:
            continue
        rank = _url_preference(origin or "", cleaned)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_url = cleaned
    return best_url


def parse_commit_object(*, raw: str, git_commit_hash: str) -> CommitMetadata:
    """Parse a raw commit object (`git cat-file -p`). No git, no fetch."""
    if not git_commit_hash:
        raise CommitParseError("missing git_commit_hash")

    headers, separator, message = raw.partition("\n\n")
    if not separator:
        raise CommitParseError("commit object has no header/message separator")

    parent_hashes: list[str] = []
    author = (None, None, None)
    committer = (None, None, None)
    for line in _header_lines(headers):
        if line.startswith("parent "):
            parent_hashes.append(line.removeprefix("parent ").strip())
        elif line.startswith("author "):
            author = _parse_ident(line.removeprefix("author "))
        elif line.startswith("committer "):
            committer = _parse_ident(line.removeprefix("committer "))

    subject = message.split("\n", 1)[0] if message else None
    if subject == "":
        subject = None

    return CommitMetadata(
        git_commit_hash=git_commit_hash,
        author_name=author[0],
        author_email=author[1],
        author_date=author[2],
        committer_name=committer[0],
        committer_email=committer[1],
        committer_date=committer[2],
        subject=subject,
        message=message if message else None,
        parent_hashes=tuple(parent_hashes),
    )


def parse_commit(*, repo_path: str, git_commit_hash: str) -> CommitMetadata:
    """Read one commit from an existing repo. Does not fetch."""
    try:
        full_hash = (
            _git(
                Path(repo_path),
                "rev-parse",
                "--verify",
                f"{git_commit_hash}^{{commit}}",
            )
            .decode()
            .strip()
        )
        raw = _git(Path(repo_path), "cat-file", "-p", full_hash).decode(
            "utf-8", errors="replace"
        )
    except FetchFailedError as exc:
        raise CommitParseError(str(exc)) from exc
    return parse_commit_object(raw=raw, git_commit_hash=full_hash)


def fetch_commit_metadata(
    git_commit_hash: str,
    url: str | None = None,
) -> CommitMetadata:
    """Fetch a single SHA into a throwaway bare repo, parse it, wipe the repo.

    Not the fill path for `commits`: no ancestry, no parent-object fetch.
    """
    remote_url = _resolve_fetch_url(git_commit_hash, url)
    scratch = Path(settings.GIT_SCRATCH_DIR)
    scratch.mkdir(parents=True, exist_ok=True)
    repo_dir = Path(tempfile.mkdtemp(prefix="commit-fetch-", dir=scratch))
    try:
        _git(repo_dir, "init", "--bare")
        _git(repo_dir, "remote", "add", "origin", remote_url)
        _git(
            repo_dir,
            "fetch",
            "--no-tags",
            "--depth=1",
            "--filter=tree:0",
            "origin",
            git_commit_hash,
            timeout=FETCH_TIMEOUT_SECONDS,
        )
        assert_single_commit_fetch(repo_dir)
        return parse_commit(repo_path=str(repo_dir), git_commit_hash=git_commit_hash)
    except CommitMetadataError:
        raise
    except Exception as exc:
        raise FetchFailedError(
            f"fetch {git_commit_hash} from {remote_url} failed: {exc}"
        ) from exc
    finally:
        shutil.rmtree(repo_dir, ignore_errors=True)


def assert_single_commit_fetch(repo_dir: Path) -> None:
    """Fail if the remote ignored shallow/filter and sent a full or treeful pack."""
    pack_bytes = _pack_bytes(repo_dir)
    if pack_bytes > MAX_EPHEMERAL_PACK_BYTES:
        raise OversizedPackError(
            f"ephemeral fetch pack is {pack_bytes} bytes (max {MAX_EPHEMERAL_PACK_BYTES})"
        )

    counts = _object_type_counts(repo_dir)
    if counts.get("tree", 0) or counts.get("blob", 0):
        raise UnexpectedFetchObjectsError(
            f"ephemeral fetch included trees/blobs: {counts}"
        )
    if counts.get("commit", 0) != 1:
        raise UnexpectedFetchObjectsError(
            f"ephemeral fetch must contain exactly one commit: {counts}"
        )


def _resolve_fetch_url(git_commit_hash: str, url: str | None) -> str:
    if url is not None:
        cleaned = sanitize_git_url(url)
        if cleaned is None:
            raise InvalidGitUrlError(f"malformed git url: {url!r}")
        return cleaned

    resolved = resolve_checkout_git_url(git_commit_hash)
    if resolved is None:
        raise MissingGitUrlError(f"no usable git url for {git_commit_hash}")
    return resolved


def _url_preference(origin: str, url: str) -> tuple[int, str]:
    host = urlparse(url).netloc.lower()
    kernel_org = "git.kernel.org" in host
    maestro = origin == "maestro"
    if maestro and kernel_org:
        tier = 0
    elif kernel_org:
        tier = 1
    elif maestro:
        tier = 2
    else:
        tier = 3
    return (tier, url)


def _header_lines(headers: str):
    for line in headers.split("\n"):
        if line.startswith(" "):
            continue
        yield line


def _parse_ident(
    ident: str,
) -> tuple[str | None, str | None, datetime | None]:
    match = _IDENT_RE.match(ident.strip())
    if match is None:
        return (None, None, None)
    name, email, unix, tz = match.groups()
    name = name.strip() or None
    email = email.strip() or None
    return (name, email, _parse_git_date(int(unix), tz))


def _parse_git_date(unix: int, tz: str) -> datetime:
    sign = 1 if tz[0] == "+" else -1
    hours = int(tz[1:3])
    minutes = int(tz[3:5])
    offset = timedelta(hours=hours, minutes=minutes) * sign
    return datetime.fromtimestamp(unix, tz=timezone(offset))


def _pack_bytes(repo_dir: Path) -> int:
    pack_dir = repo_dir / "objects" / "pack"
    if not pack_dir.is_dir():
        return 0
    return sum(
        path.stat().st_size for path in pack_dir.glob("*.pack") if path.is_file()
    )


def _object_type_counts(repo_dir: Path) -> dict[str, int]:
    output = _git(
        repo_dir,
        "cat-file",
        "--batch-check=%(objecttype)",
        "--batch-all-objects",
    ).decode()
    counts: dict[str, int] = {}
    for line in output.splitlines():
        object_type = line.strip()
        if object_type:
            counts[object_type] = counts.get(object_type, 0) + 1
    return counts


def _git_executable() -> str:
    git = shutil.which("git")
    if git is None:
        raise FetchFailedError("git executable not found")
    return git


def _git(repo_dir: Path, *args: str, timeout: int = 30) -> bytes:
    env = os.environ.copy()
    env.update(_GIT_ENV)
    command = [_git_executable(), "-C", str(repo_dir), *args]
    try:
        result = subprocess.run(  # noqa: S603
            command,
            check=False,
            capture_output=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise FetchFailedError(f"git {' '.join(args)} timed out") from exc

    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise FetchFailedError(f"git {' '.join(args)} failed: {stderr}")
    return result.stdout
