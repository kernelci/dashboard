"""Fill `commits` / `commit_parents` from a persistent treeless mirror (#2109).

Parse uses the existing-repo helper from #2090. One-shot SHA fetch is only
the optional gap-fill for hashes the mirror does not cover.
"""

from __future__ import annotations

import hashlib
import logging
import tempfile
import time
from collections.abc import Iterator, Sequence
from enum import Enum
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
INSERT_BATCH_SIZE = 1000
DEFAULT_FETCH_TIMEOUT_SECONDS = 1800
REV_LIST_TIMEOUT_SECONDS = 3600
# One `cat-file --batch` process per chunk instead of two per commit. Chunked so a
# full-history import streams to the DB instead of buffering every message in RAM.
PARSE_BATCH_SIZE = 2000
CAT_FILE_TIMEOUT_SECONDS = 600
PROGRESS_LOG_EVERY = 20000
# Runaway backstop only. A treeless mainline pack is ~850MB; an unfiltered one
# (git.kernel.org cannot filter) is ~3.5GB. Both are legitimate first fetches.
MAX_REMOTE_PACK_BYTES = 6 * 1024 * 1024 * 1024
LS_REMOTE_TIMEOUT_SECONDS = 300
FETCH_ATTEMPTS = 2
# The more trees the mirror holds, the more `have` lines negotiation carries, and
# git.kernel.org's frontend starts answering HTTP 400. Unchunked HTTP/1.1 gets
# through; the low-speed deadline keeps git from sitting on the dead connection
# afterwards. Auto-gc would repack a multi-GB mirror in the middle of a run.
MIRROR_GIT_CONFIG = {
    "http.version": "HTTP/1.1",
    "http.postBuffer": str(512 * 1024 * 1024),
    "http.lowSpeedLimit": "1000",
    "http.lowSpeedTime": "60",
    "gc.auto": "0",
}


class FetchOutcome(Enum):
    OK = "ok"
    FAILED = "failed"
    REJECTED = "rejected"


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
    if not (repo_dir / "HEAD").exists():
        run_git(repo_dir, "init", "--bare")
    for key, value in MIRROR_GIT_CONFIG.items():
        run_git(repo_dir, "config", key, value)


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


def checkout_branches_by_url() -> dict[str, set[str]]:
    """Branches we already see in checkouts, keyed by sanitized git url."""
    mapping: dict[str, set[str]] = {}
    try:
        rows = (
            Checkouts.objects.filter(git_repository_url__isnull=False)
            .exclude(git_repository_branch="")
            .values_list("git_repository_url", "git_repository_branch")
            .distinct()
        )
        for raw_url, branch in rows:
            if not branch:
                continue
            cleaned = sanitize_git_url(raw_url)
            if cleaned is None:
                continue
            mapping.setdefault(cleaned, set()).add(branch)
    except Exception as exc:
        logger.warning("could not read checkout branches: %s", exc)
    return mapping


def fetch_remote(
    repo_dir: Path,
    *,
    url: str,
    timeout: int = DEFAULT_FETCH_TIMEOUT_SECONDS,
    verbose_git: bool = False,
    branches: set[str] | None = None,
    skip_unfilterable: bool = False,
) -> bool:
    """Fetch the checkout branches of one remote into the shared mirror.

    Servers that cannot filter (git.kernel.org advertises only `fetch=shallow`)
    send trees and blobs. We still take them: objects are shared across remotes,
    so only the first kernel tree is expensive. `skip_unfilterable` opts out.
    """
    name = remote_name_for_url(url)
    wanted = (
        branches if branches is not None else checkout_branches_by_url().get(url, set())
    )
    try:
        _ensure_remote(repo_dir, name=name, url=url)
        available, supports_filter = _probe_remote(repo_dir, name)
        _configure_promisor(repo_dir, name=name, enabled=supports_filter)
    except CommitMetadataError as exc:
        logger.warning("skip remote %s (%s): %s", name, url, exc)
        return False

    if not supports_filter:
        if skip_unfilterable:
            out("  server cannot filter; skipping (--skip-unfilterable)")
            logger.warning("skip remote %s (%s): server cannot filter", name, url)
            return False
        out("  server cannot filter; fetching with trees/blobs")

    branch_specs = _branch_refspecs(name, wanted, available)
    if branch_specs:
        out(f"  refs: {len(branch_specs)} checkout branch(es)")
    else:
        out("  no checkout branch on this remote; fetching HEAD only")
        branch_specs = [f"+HEAD:refs/remotes/{name}/HEAD"]

    for attempt in range(1, FETCH_ATTEMPTS + 1):
        outcome = _fetch_refspecs_or_rollback(
            repo_dir,
            name=name,
            url=url,
            refspecs=branch_specs,
            timeout=timeout,
            verbose_git=verbose_git,
            use_filter=supports_filter,
        )
        if outcome is FetchOutcome.OK:
            return True
        if outcome is FetchOutcome.REJECTED:
            # Same server, same filter behaviour: a retry downloads it all again.
            logger.warning("skip remote %s (%s) this run: pack rejected", name, url)
            return False
        # A dropped connection mid-negotiation is the common failure, and the objects
        # that already landed are still there, so the retry resumes instead of redoing.
        if attempt < FETCH_ATTEMPTS:
            out(f"  fetch failed; retrying ({attempt + 1}/{FETCH_ATTEMPTS})")

    logger.warning("skip remote %s (%s) this run: fetch failed", name, url)
    return False


def mirror_size_bytes(repo_dir: Path) -> int:
    if not repo_dir.is_dir():
        return 0
    return sum(path.stat().st_size for path in repo_dir.rglob("*") if path.is_file())


def new_commit_hashes(repo_dir: Path, old_tips: Sequence[str]) -> list[str]:
    args = ["rev-list", "--reverse", "--topo-order", "--remotes"]
    stdin: bytes | None = None
    if old_tips:
        # `--not --stdin` does *not* mark stdin lines uninteresting (git treats
        # `--not` as applying to the next CLI revision, and `--stdin` is a flag).
        # Prefix each tip with `^` instead, which rev-list does honour on stdin.
        args.append("--stdin")
        stdin = "".join(f"^{tip}\n" for tip in old_tips).encode()
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


def insert_commits(metadatas: Sequence[CommitMetadata]) -> tuple[int, int]:
    """Insert commits then parent edges. Existing rows are left alone.

    A git object is immutable, so a hash that is already stored is not updated.
    No stubs. Callers pass topo order.
    """
    commit_count = 0
    edge_count = 0
    for start in range(0, len(metadatas), INSERT_BATCH_SIZE):
        batch = metadatas[start : start + INSERT_BATCH_SIZE]
        commits, edges = _insert_batch(batch)
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
            commits, _edges = insert_commits([metadata])
            written += commits
        if index % 100 == 0 or index == len(gaps):
            out(f"gaps {index}/{len(gaps)}: {fetched} fetched, {written} written")
    return fetched, written


def _fetch_allowlisted_trees(
    repo_dir: Path,
    *,
    dry_run: bool,
    fetch_timeout: int,
    verbose_git: bool,
    skip_unfilterable: bool,
    size_before: int,
) -> tuple[int, int]:
    remotes_ok = 0
    remotes_failed = 0
    out("resolving tree allowlist...")
    urls = allowlisted_tree_urls(refresh=not dry_run)
    if not urls:
        logger.warning(
            "no allowlisted tree urls in %s; run `manage.py treeproof`",
            TREE_NAMES_FILENAME,
        )
    out(f"fetching {len(urls)} trees (checkout branches only, treeless)")
    branches_by_url = checkout_branches_by_url()
    for index, url in enumerate(urls, start=1):
        out(f"[{index}/{len(urls)}] fetching {url}")
        started = time.monotonic()
        succeeded = fetch_remote(
            repo_dir,
            url=url,
            timeout=fetch_timeout,
            verbose_git=verbose_git,
            branches=branches_by_url.get(url, set()),
            skip_unfilterable=skip_unfilterable,
        )
        elapsed = time.monotonic() - started
        if succeeded:
            remotes_ok += 1
            out(f"[{index}/{len(urls)}] done in {elapsed:.0f}s")
        else:
            remotes_failed += 1
            out(f"[{index}/{len(urls)}] failed after {elapsed:.0f}s, moving on")
    grew = mirror_size_bytes(repo_dir) - size_before
    out(
        f"fetch finished: {remotes_ok} ok, {remotes_failed} failed, "
        f"mirror grew {_human_bytes(grew)}"
    )
    return remotes_ok, remotes_failed


def _ingest_new_commits(
    repo_dir: Path, old_tips: Sequence[str], *, dry_run: bool
) -> tuple[int, int, int]:
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
            commits, edges = insert_commits(batch)
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
    return parsed, commits_written, edges_written


def sync_commit_metadata(
    *,
    mirror_dir: Path | None = None,
    dry_run: bool = False,
    skip_fetch: bool = False,
    skip_ingest: bool = False,
    fill_gaps: bool = False,
    fetch_timeout: int = DEFAULT_FETCH_TIMEOUT_SECONDS,
    verbose_git: bool = False,
    skip_unfilterable: bool = False,
) -> dict[str, int]:
    if skip_fetch and skip_ingest:
        raise ValueError("skip_fetch and skip_ingest cannot both be set")

    repo_dir = Path(mirror_dir or settings.GIT_MIRROR_DIR)
    ensure_mirror(repo_dir)
    old_tips = read_stored_tips(repo_dir)
    size_before = mirror_size_bytes(repo_dir)
    out(
        f"mirror={repo_dir} size={_human_bytes(size_before)} "
        f"known_tips={len(old_tips)} dry_run={dry_run} "
        f"skip_fetch={skip_fetch} skip_ingest={skip_ingest}"
    )

    remotes_ok = 0
    remotes_failed = 0
    if skip_fetch:
        out("skipping fetch, using objects already in the mirror")
    else:
        remotes_ok, remotes_failed = _fetch_allowlisted_trees(
            repo_dir,
            dry_run=dry_run,
            fetch_timeout=fetch_timeout,
            verbose_git=verbose_git,
            skip_unfilterable=skip_unfilterable,
            size_before=size_before,
        )

    empty = {
        "remotes_ok": remotes_ok,
        "remotes_failed": remotes_failed,
        "parsed": 0,
        "commits_written": 0,
        "edges_written": 0,
        "gaps_fetched": 0,
        "gaps_written": 0,
    }
    if skip_ingest:
        out("skipping ingest; tips unchanged")
        return empty

    parsed, commits_written, edges_written = _ingest_new_commits(
        repo_dir, old_tips, dry_run=dry_run
    )
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


def _human_bytes(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if abs(size) < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TiB"


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


def _probe_remote(repo_dir: Path, name: str) -> tuple[set[str], bool]:
    """Return (branch names, server supports partial-clone filter).

    One ls-remote answers both. Capabilities are only exposed in git's packet
    trace, so we point GIT_TRACE_PACKET at a file and read the `fetch=` line.
    """
    with tempfile.TemporaryDirectory() as scratch:
        trace = Path(scratch) / "packet-trace"
        try:
            output = run_git(
                repo_dir,
                "-c",
                "protocol.version=2",
                "ls-remote",
                "--heads",
                name,
                timeout=LS_REMOTE_TIMEOUT_SECONDS,
                extra_env={"GIT_TRACE_PACKET": str(trace)},
            ).decode()
        except CommitMetadataError as exc:
            logger.warning("ls-remote %s failed: %s", name, exc)
            return set(), False
        supports_filter = _trace_advertises_filter(trace)

    heads: set[str] = set()
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 2 or not parts[1].startswith("refs/heads/"):
            continue
        heads.add(parts[1].removeprefix("refs/heads/"))
    return heads, supports_filter


def _trace_advertises_filter(trace: Path) -> bool:
    if not trace.is_file():
        return False
    for line in trace.read_text(errors="replace").splitlines():
        _, separator, capability = line.partition("fetch=")
        if separator and "filter" in capability.split():
            return True
    return False


def _branch_refspecs(name: str, wanted: set[str], available: set[str]) -> list[str]:
    if not wanted:
        return []
    names = sorted(wanted & available) if available else sorted(wanted)
    return [f"+refs/heads/{branch}:refs/remotes/{name}/{branch}" for branch in names]


def _fetch_refspecs_or_rollback(
    repo_dir: Path,
    *,
    name: str,
    url: str,
    refspecs: list[str],
    timeout: int,
    verbose_git: bool,
    use_filter: bool = True,
) -> FetchOutcome:
    packs_before = _pack_paths(repo_dir)
    refs_before = _remote_refs(repo_dir, name)
    try:
        run_git(
            repo_dir,
            "fetch",
            "--prune",
            "--no-tags",
            *(["--filter=tree:0"] if use_filter else []),
            *(["--progress"] if verbose_git else []),
            name,
            *refspecs,
            timeout=timeout,
            stream=verbose_git,
        )
    except CommitMetadataError as exc:
        logger.warning("fetch %s (%s) failed: %s", name, url, exc)
        _rollback_fetch(
            repo_dir,
            name=name,
            packs_before=packs_before,
            refs_before=refs_before,
            keep_packs=True,
        )
        return FetchOutcome.FAILED

    reason = _new_packs_rejected(repo_dir, packs_before, expect_treeless=use_filter)
    if reason is None:
        return FetchOutcome.OK

    logger.warning("reject pack from %s (%s): %s", name, url, reason)
    _rollback_fetch(
        repo_dir, name=name, packs_before=packs_before, refs_before=refs_before
    )
    return FetchOutcome.REJECTED


def _pack_paths(repo_dir: Path) -> set[Path]:
    pack_dir = repo_dir / "objects" / "pack"
    if not pack_dir.is_dir():
        return set()
    return {path for path in pack_dir.iterdir() if path.is_file()}


def _remote_refs(repo_dir: Path, name: str) -> dict[str, str]:
    try:
        output = run_git(
            repo_dir,
            "for-each-ref",
            "--format=%(objectname) %(refname)",
            f"refs/remotes/{name}",
        ).decode()
    except FetchFailedError:
        return {}
    refs: dict[str, str] = {}
    for line in output.splitlines():
        sha, _, ref = line.partition(" ")
        if sha and ref:
            refs[ref] = sha
    return refs


def _rollback_fetch(
    repo_dir: Path,
    *,
    name: str,
    packs_before: set[Path],
    refs_before: dict[str, str],
    keep_packs: bool = False,
) -> None:
    """Restore refs, and drop the new packs unless the caller wants to keep them.

    A pack that finished writing holds valid objects even when the fetch died
    afterwards, and git shares them with every other remote. Deleting it means
    paying for the same download again; only the unfinished `tmp_pack_*` is junk.
    """
    current_refs = _remote_refs(repo_dir, name)
    for ref in current_refs:
        if ref not in refs_before:
            try:
                run_git(repo_dir, "update-ref", "-d", ref)
            except FetchFailedError as exc:
                logger.warning("could not drop ref %s: %s", ref, exc)
    for ref, sha in refs_before.items():
        try:
            run_git(repo_dir, "update-ref", ref, sha)
        except FetchFailedError as exc:
            logger.warning("could not restore ref %s: %s", ref, exc)

    for path in _pack_paths(repo_dir) - packs_before:
        if keep_packs and not path.name.startswith("tmp_pack"):
            continue
        try:
            path.unlink()
        except OSError as exc:
            logger.warning("could not remove %s: %s", path, exc)


def _new_packs_rejected(
    repo_dir: Path, packs_before: set[Path], *, expect_treeless: bool
) -> str | None:
    for path in sorted(_pack_paths(repo_dir) - packs_before):
        reason = _pack_rejection_reason(repo_dir, path, expect_treeless=expect_treeless)
        if reason is not None:
            return reason
    return None


def _pack_rejection_reason(
    repo_dir: Path, path: Path, *, expect_treeless: bool
) -> str | None:
    if path.name.startswith("tmp_pack"):
        return f"incomplete pack {path.name}"
    if path.suffix != ".pack":
        return None

    size = path.stat().st_size
    if size > MAX_REMOTE_PACK_BYTES:
        return f"{path.name} is {size} bytes (max {MAX_REMOTE_PACK_BYTES})"

    if not expect_treeless:
        return None

    idx = path.with_suffix(".idx")
    if not idx.is_file():
        return f"{path.name} has no index"

    # The server said it could filter, so trees/blobs mean it did not honour it.
    types = _pack_object_types(repo_dir, idx)
    leaked = types & {"tree", "blob"}
    if leaked:
        return f"{path.name} contains {', '.join(sorted(leaked))}"
    return None


def _pack_object_types(repo_dir: Path, idx: Path) -> set[str]:
    try:
        output = run_git(
            repo_dir,
            "verify-pack",
            "-v",
            str(idx.relative_to(repo_dir)),
            timeout=120,
        ).decode()
    except (CommitMetadataError, ValueError) as exc:
        logger.warning("verify-pack %s failed: %s", idx, exc)
        return set()
    types: set[str] = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[1] in {"commit", "tree", "blob", "tag"}:
            types.add(fields[1])
    return types


def _ensure_remote(repo_dir: Path, *, name: str, url: str) -> None:
    existing = _remote_urls(repo_dir)
    if name not in existing:
        run_git(repo_dir, "remote", "add", name, url)
    elif existing[name] != url:
        run_git(repo_dir, "remote", "set-url", name, url)


def _configure_promisor(repo_dir: Path, *, name: str, enabled: bool) -> None:
    for key, value in (("promisor", "true"), ("partialclonefilter", "tree:0")):
        try:
            if enabled:
                run_git(repo_dir, "config", f"remote.{name}.{key}", value)
            else:
                run_git(repo_dir, "config", "--unset", f"remote.{name}.{key}")
        except FetchFailedError:
            # `--unset` exits non-zero when the key was never set.
            pass


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


def _insert_batch(metadatas: Sequence[CommitMetadata]) -> tuple[int, int]:
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
        rows, ignore_conflicts=True, batch_size=INSERT_BATCH_SIZE
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
            edges, ignore_conflicts=True, batch_size=INSERT_BATCH_SIZE
        )
    return len(metadatas), len(edges)
