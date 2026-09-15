"""Fill `commits` / `commit_parents` from a persistent treeless mirror (#2109).

Parse uses the existing-repo helper from #2090. One-shot SHA fetch is only
the optional gap-fill for hashes the mirror does not cover.
"""

from __future__ import annotations

import hashlib
import logging
import time
from collections.abc import Iterator, Sequence
from pathlib import Path

from django.conf import settings

from kernelCI_app.constants.tree_names import TREE_NAMES_FILENAME
from kernelCI_app.helpers.gitCommit import (
    CommitMetadata,
    CommitMetadataError,
    FetchFailedError,
    fetch_commit_metadata,
    parse_commit_object,
    run_git,
    sanitize_git_url,
)
from kernelCI_app.helpers.logger import out
from kernelCI_app.helpers.trees import get_tree_file_data
from kernelCI_app.management.commands.treeproof import Command as TreeproofCommand
from kernelCI_app.models import Checkouts, CommitParents, Commits

logger = logging.getLogger(__name__)

TIPS_FILENAME = "synced-tips"
UPSERT_BATCH_SIZE = 1000
DEFAULT_FETCH_TIMEOUT_SECONDS = 1800
REV_LIST_TIMEOUT_SECONDS = 3600
# One `cat-file --batch` process per chunk instead of two per commit. Chunked so a
# full-history import streams to the DB instead of buffering every message in RAM.
PARSE_BATCH_SIZE = 2000
CAT_FILE_TIMEOUT_SECONDS = 600
PROGRESS_LOG_EVERY = 20000


def allowlisted_tree_urls(*, refresh: bool = True) -> list[str]:
    """Known-good tree URLs from treeproof, not per-hash checkout git_repository_url.

    Regenerates the mapping like the ingester does, so the job does not silently
    no-op when nobody ran `treeproof` on this volume yet.
    """
    file_data = (
        TreeproofCommand().generate_tree_names() if refresh else get_tree_file_data()
    )
    trees = file_data.get("trees") if isinstance(file_data, dict) else None
    if not isinstance(trees, dict):
        return []

    urls: list[str] = []
    seen: set[str] = set()
    for tree_data in trees.values():
        raw = tree_data.get("url") if isinstance(tree_data, dict) else None
        cleaned = sanitize_git_url(raw)
        if cleaned is None or cleaned in seen:
            continue
        seen.add(cleaned)
        urls.append(cleaned)
    return urls


def remote_name_for_url(url: str) -> str:
    return "r" + hashlib.sha256(url.encode()).hexdigest()[:16]


def ensure_mirror(repo_dir: Path) -> None:
    repo_dir.mkdir(parents=True, exist_ok=True)
    if (repo_dir / "HEAD").exists():
        return
    run_git(repo_dir, "init", "--bare")


def list_tips(repo_dir: Path) -> tuple[str, ...]:
    output = run_git(
        repo_dir, "for-each-ref", "--format=%(objectname)", "refs/remotes"
    ).decode()
    return tuple(sorted({line.strip() for line in output.splitlines() if line.strip()}))


def read_stored_tips(repo_dir: Path) -> tuple[str, ...]:
    path = repo_dir / TIPS_FILENAME
    if not path.is_file():
        return ()
    return tuple(line.strip() for line in path.read_text().splitlines() if line.strip())


def write_stored_tips(repo_dir: Path, tips: Sequence[str]) -> None:
    text = "\n".join(tips)
    if text:
        text += "\n"
    (repo_dir / TIPS_FILENAME).write_text(text)


def fetch_remote(
    repo_dir: Path,
    *,
    url: str,
    timeout: int = DEFAULT_FETCH_TIMEOUT_SECONDS,
    verbose_git: bool = False,
) -> bool:
    name = remote_name_for_url(url)
    try:
        _ensure_remote(repo_dir, name=name, url=url)
        run_git(
            repo_dir,
            "fetch",
            "--prune",
            "--no-tags",
            "--filter=tree:0",
            *(["--progress"] if verbose_git else []),
            name,
            timeout=timeout,
            stream=verbose_git,
        )
        return True
    except CommitMetadataError as exc:
        logger.warning("skip remote %s (%s): %s", name, url, exc)
        return False


def new_commit_hashes(repo_dir: Path, old_tips: Sequence[str]) -> list[str]:
    args = ["rev-list", "--reverse", "--topo-order", "--remotes"]
    stdin: bytes | None = None
    if old_tips:
        args.extend(["--not", "--stdin"])
        stdin = ("\n".join(old_tips) + "\n").encode()
    try:
        output = run_git(
            repo_dir, *args, timeout=REV_LIST_TIMEOUT_SECONDS, stdin=stdin
        ).decode()
    except FetchFailedError as exc:
        logger.warning("rev-list failed: %s", exc)
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def iter_parsed_commits(
    repo_dir: Path, hashes: Sequence[str]
) -> Iterator[list[CommitMetadata]]:
    """Yield parsed commits in chunks, keeping rev-list's topological order."""
    for start in range(0, len(hashes), PARSE_BATCH_SIZE):
        chunk = hashes[start : start + PARSE_BATCH_SIZE]
        stdin = ("\n".join(chunk) + "\n").encode()
        try:
            raw = run_git(
                repo_dir,
                "cat-file",
                "--batch",
                stdin=stdin,
                timeout=CAT_FILE_TIMEOUT_SECONDS,
            )
        except FetchFailedError as exc:
            logger.warning("skip batch starting at %s: %s", chunk[0], exc)
            continue
        yield _parse_batch_output(raw)


def parse_commits(repo_dir: Path, hashes: Sequence[str]) -> list[CommitMetadata]:
    return [
        metadata
        for batch in iter_parsed_commits(repo_dir, hashes)
        for metadata in batch
    ]


def upsert_commits(metadatas: Sequence[CommitMetadata]) -> tuple[int, int]:
    """Insert commits then parent edges. No stubs. Callers pass topo order."""
    commit_count = 0
    edge_count = 0
    for start in range(0, len(metadatas), UPSERT_BATCH_SIZE):
        batch = metadatas[start : start + UPSERT_BATCH_SIZE]
        commits, edges = _upsert_batch(batch)
        commit_count += commits
        edge_count += edges
    return commit_count, edge_count


def missing_checkout_hashes() -> list[str]:
    existing = Commits.objects.values("git_commit_hash")
    return list(
        Checkouts.objects.filter(git_commit_hash__isnull=False)
        .exclude(git_commit_hash__in=existing)
        .values_list("git_commit_hash", flat=True)
        .distinct()
    )


def fill_checkout_gaps(*, dry_run: bool = False) -> tuple[int, int]:
    """One-shot SHA fetch (#2090) for checkout hashes the mirror missed."""
    out("looking for checkout hashes still missing from commits...")
    gaps = missing_checkout_hashes()
    out(f"{len(gaps)} checkout hashes to fetch one by one")

    fetched = 0
    written = 0
    for index, git_commit_hash in enumerate(gaps, start=1):
        try:
            metadata = fetch_commit_metadata(git_commit_hash)
        except CommitMetadataError as exc:
            logger.warning("skip gap %s: %s", git_commit_hash, exc)
            continue
        fetched += 1
        if not dry_run:
            commits, _edges = upsert_commits([metadata])
            written += commits
        if index % 100 == 0 or index == len(gaps):
            out(f"gaps {index}/{len(gaps)}: {fetched} fetched, {written} written")
    return fetched, written


def sync_commit_metadata(
    *,
    mirror_dir: Path | None = None,
    dry_run: bool = False,
    skip_fetch: bool = False,
    fill_gaps: bool = False,
    fetch_timeout: int = DEFAULT_FETCH_TIMEOUT_SECONDS,
    verbose_git: bool = False,
) -> dict[str, int]:
    repo_dir = Path(mirror_dir or settings.GIT_MIRROR_DIR)
    ensure_mirror(repo_dir)
    old_tips = read_stored_tips(repo_dir)
    out(
        f"mirror={repo_dir} known_tips={len(old_tips)} "
        f"dry_run={dry_run} skip_fetch={skip_fetch}"
    )

    remotes_ok = 0
    remotes_failed = 0
    if skip_fetch:
        out("skipping fetch, using objects already in the mirror")
    else:
        out("resolving tree allowlist...")
        urls = allowlisted_tree_urls(refresh=not dry_run)
        if not urls:
            logger.warning(
                "no allowlisted tree urls in %s; run `manage.py treeproof`",
                TREE_NAMES_FILENAME,
            )
        out(f"fetching {len(urls)} trees (first run clones full history, be patient)")
        for index, url in enumerate(urls, start=1):
            out(f"[{index}/{len(urls)}] fetching {url}")
            started = time.monotonic()
            succeeded = fetch_remote(
                repo_dir, url=url, timeout=fetch_timeout, verbose_git=verbose_git
            )
            elapsed = time.monotonic() - started
            if succeeded:
                remotes_ok += 1
                out(f"[{index}/{len(urls)}] done in {elapsed:.0f}s")
            else:
                remotes_failed += 1
                out(f"[{index}/{len(urls)}] failed after {elapsed:.0f}s, moving on")
        out(f"fetch finished: {remotes_ok} ok, {remotes_failed} failed")

    out("enumerating new commit objects...")
    started = time.monotonic()
    hashes = new_commit_hashes(repo_dir, old_tips)
    out(
        f"{len(hashes)} new commits to ingest "
        f"(enumerated in {time.monotonic() - started:.0f}s)"
    )

    parsed = 0
    commits_written = 0
    edges_written = 0
    logged_at = 0
    for batch in iter_parsed_commits(repo_dir, hashes):
        parsed += len(batch)
        if not dry_run:
            commits, edges = upsert_commits(batch)
            commits_written += commits
            edges_written += edges
        if parsed - logged_at >= PROGRESS_LOG_EVERY or parsed == len(hashes):
            logged_at = parsed
            out(
                f"parsed {parsed}/{len(hashes)} commits, "
                f"wrote {commits_written} commits and {edges_written} parent edges"
            )

    if not dry_run:
        write_stored_tips(repo_dir, list_tips(repo_dir))
        out("tips recorded; next run only ingests what is new")

    gaps_fetched = 0
    gaps_written = 0
    if fill_gaps:
        gaps_fetched, gaps_written = fill_checkout_gaps(dry_run=dry_run)

    return {
        "remotes_ok": remotes_ok,
        "remotes_failed": remotes_failed,
        "parsed": parsed,
        "commits_written": commits_written,
        "edges_written": edges_written,
        "gaps_fetched": gaps_fetched,
        "gaps_written": gaps_written,
    }


def _parse_batch_output(raw: bytes) -> list[CommitMetadata]:
    """Split `cat-file --batch` records: `<oid> <type> <size>\\n<payload>\\n`."""
    parsed: list[CommitMetadata] = []
    offset = 0
    while offset < len(raw):
        line_end = raw.find(b"\n", offset)
        if line_end == -1:
            break
        header = raw[offset:line_end].decode("utf-8", errors="replace")
        offset = line_end + 1

        fields = header.split()
        if len(fields) < 3:
            # "<oid> missing" / "<oid> ambiguous": no payload follows.
            logger.warning("skip cat-file entry: %s", header)
            continue

        oid, object_type, size_text = fields[0], fields[1], fields[2]
        try:
            size = int(size_text)
        except ValueError:
            logger.warning("unparseable cat-file header, dropping batch: %s", header)
            break

        payload = raw[offset : offset + size]
        offset += size + 1
        if object_type != "commit":
            continue

        try:
            parsed.append(
                parse_commit_object(
                    raw=payload.decode("utf-8", errors="replace"), git_commit_hash=oid
                )
            )
        except CommitMetadataError as exc:
            logger.warning("skip parse %s: %s", oid, exc)
    return parsed


def _ensure_remote(repo_dir: Path, *, name: str, url: str) -> None:
    existing = _remote_urls(repo_dir)
    if name not in existing:
        run_git(repo_dir, "remote", "add", name, url)
        return
    if existing[name] != url:
        run_git(repo_dir, "remote", "set-url", name, url)


def _remote_urls(repo_dir: Path) -> dict[str, str]:
    try:
        output = run_git(repo_dir, "remote", "-v").decode()
    except FetchFailedError:
        return {}
    urls: dict[str, str] = {}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] not in urls:
            urls[parts[0]] = parts[1]
    return urls


def _upsert_batch(metadatas: Sequence[CommitMetadata]) -> tuple[int, int]:
    rows = [
        Commits(
            git_commit_hash=metadata.git_commit_hash,
            author_name=metadata.author_name,
            author_email=metadata.author_email,
            author_date=metadata.author_date,
            committer_name=metadata.committer_name,
            committer_email=metadata.committer_email,
            committer_date=metadata.committer_date,
            subject=metadata.subject,
            message=metadata.message,
        )
        for metadata in metadatas
    ]
    Commits.objects.bulk_create(
        rows, ignore_conflicts=True, batch_size=UPSERT_BATCH_SIZE
    )

    hashes = {metadata.git_commit_hash for metadata in metadatas}
    for metadata in metadatas:
        hashes.update(metadata.parent_hashes)
    hash_to_id = dict(
        Commits.objects.filter(git_commit_hash__in=hashes).values_list(
            "git_commit_hash", "id"
        )
    )

    edges: list[CommitParents] = []
    for metadata in metadatas:
        commit_id = hash_to_id.get(metadata.git_commit_hash)
        if commit_id is None:
            continue
        for ord_, parent_hash in enumerate(metadata.parent_hashes):
            parent_id = hash_to_id.get(parent_hash)
            if parent_id is None:
                logger.warning(
                    "skip parent edge %s -> %s (parent not in commits)",
                    metadata.git_commit_hash,
                    parent_hash,
                )
                continue
            edges.append(
                CommitParents(commit_id=commit_id, parent_id=parent_id, ord=ord_)
            )

    if edges:
        CommitParents.objects.bulk_create(
            edges, ignore_conflicts=True, batch_size=UPSERT_BATCH_SIZE
        )
    return len(metadatas), len(edges)
