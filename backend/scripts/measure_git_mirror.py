#!/usr/bin/env python3
"""Grow a bare mirror the same way sync_commit_mirror fetches, and print disk after each URL.

No Django, no DB writes. Reads one git URL per line (comments and blanks skipped).

Without checkout branches we fetch HEAD only — the job's fallback, and the bulk of
object-store growth. Extra checkout branches mostly share those objects.

Pack rejection is skipped on purpose: a 3.5GB kernel.org pack is what we want to see.

  python3 backend/scripts/measure_git_mirror.py --urls urls.txt --mirror-dir /tmp/git-mirror
"""

from __future__ import annotations

import argparse
import hashlib
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_FETCH_TIMEOUT = 1800
LS_REMOTE_TIMEOUT = 300


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--urls",
        type=Path,
        required=True,
        help="Text file: one git URL per line.",
    )
    parser.add_argument(
        "--mirror-dir",
        type=Path,
        default=Path("/tmp/kernelci-git-mirror-measure"),
        help="Persistent bare repo (created if missing).",
    )
    parser.add_argument("--fetch-timeout", type=int, default=DEFAULT_FETCH_TIMEOUT)
    parser.add_argument(
        "--skip-unfilterable",
        action="store_true",
        help="Skip servers that do not advertise protocol-v2 filter (job flag).",
    )
    parser.add_argument(
        "--all-heads",
        action="store_true",
        help="Fetch every remote branch instead of HEAD only (upper bound).",
    )
    args = parser.parse_args()

    urls = _read_urls(args.urls)
    if not urls:
        print("no urls in", args.urls, file=sys.stderr)
        return 1

    repo = args.mirror_dir
    _ensure_bare(repo)
    print(f"mirror={repo} urls={len(urls)} start={_human(_du(repo))}", flush=True)

    ok = failed = skipped = 0
    for index, url in enumerate(urls, start=1):
        before = _du(repo)
        t0 = time.monotonic()
        print(f"\n[{index}/{len(urls)}] {url}", flush=True)
        status = _fetch_one(
            repo,
            url,
            timeout=args.fetch_timeout,
            skip_unfilterable=args.skip_unfilterable,
            all_heads=args.all_heads,
        )
        elapsed = time.monotonic() - t0
        after = _du(repo)
        print(
            f"  {status}  +{_human(after - before)}  total={_human(after)}  {elapsed:.0f}s",
            flush=True,
        )
        if status == "ok":
            ok += 1
        elif status == "skipped":
            skipped += 1
        else:
            failed += 1

    print(
        f"\ndone ok={ok} failed={failed} skipped={skipped} total={_human(_du(repo))}",
        flush=True,
    )
    return 0 if failed == 0 else 1


def _read_urls(path: Path) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        url = line.rstrip("/")
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls


def _ensure_bare(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    if not (repo / "HEAD").exists():
        _git(repo, "init", "--bare")
    # As the shared mirror grows, negotiation POSTs carry more `have` lines and
    # git.kernel.org's frontend answers HTTP 400. Unchunked HTTP/1.1 gets through.
    _git(repo, "config", "http.version", "HTTP/1.1")
    _git(repo, "config", "http.postBuffer", str(512 * 1024 * 1024))
    # After that 400, git sits on the dead connection instead of exiting. Give curl
    # a stall deadline, and keep auto-gc from repacking a multi-GB mirror mid-run.
    _git(repo, "config", "http.lowSpeedLimit", "1000")
    _git(repo, "config", "http.lowSpeedTime", "60")
    _git(repo, "config", "gc.auto", "0")


def _fetch_one(
    repo: Path,
    url: str,
    *,
    timeout: int,
    skip_unfilterable: bool,
    all_heads: bool,
) -> str:
    name = "r" + hashlib.sha256(url.encode()).hexdigest()[:16]
    try:
        _ensure_remote(repo, name, url)
        heads, supports_filter = _probe(repo, name)
        _configure_promisor(repo, name, enabled=supports_filter)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"  probe failed: {exc}", flush=True)
        return "failed"

    if not supports_filter:
        print("  server cannot filter; fetching with trees/blobs", flush=True)
        if skip_unfilterable:
            return "skipped"
    else:
        print("  filter=tree:0", flush=True)

    if all_heads and heads:
        refspecs = [
            f"+refs/heads/{branch}:refs/remotes/{name}/{branch}"
            for branch in sorted(heads)
        ]
        print(f"  refs: {len(refspecs)} heads", flush=True)
    else:
        refspecs = [f"+HEAD:refs/remotes/{name}/HEAD"]
        print("  refs: HEAD only", flush=True)

    cmd = [
        "fetch",
        "--prune",
        "--no-tags",
        *(["--filter=tree:0"] if supports_filter else []),
        "--progress",
        name,
        *refspecs,
    ]
    try:
        _git(repo, *cmd, timeout=timeout, stream=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"  fetch failed: {exc}", flush=True)
        return "failed"
    return "ok"


def _ensure_remote(repo: Path, name: str, url: str) -> None:
    existing = _remote_urls(repo)
    if name not in existing:
        _git(repo, "remote", "add", name, url)
    elif existing[name] != url:
        _git(repo, "remote", "set-url", name, url)


def _configure_promisor(repo: Path, name: str, *, enabled: bool) -> None:
    for key, value in (("promisor", "true"), ("partialclonefilter", "tree:0")):
        if enabled:
            _git(repo, "config", f"remote.{name}.{key}", value)
        else:
            try:
                _git(repo, "config", "--unset", f"remote.{name}.{key}")
            except subprocess.CalledProcessError:
                pass


def _remote_urls(repo: Path) -> dict[str, str]:
    try:
        output = _git(repo, "remote", "-v").decode()
    except subprocess.CalledProcessError:
        return {}
    urls: dict[str, str] = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 2:
            urls[fields[0]] = fields[1]
    return urls


def _probe(repo: Path, name: str) -> tuple[set[str], bool]:
    with tempfile.TemporaryDirectory() as scratch:
        trace = Path(scratch) / "packet-trace"
        output = _git(
            repo,
            "-c",
            "protocol.version=2",
            "ls-remote",
            "--heads",
            name,
            timeout=LS_REMOTE_TIMEOUT,
            extra_env={"GIT_TRACE_PACKET": str(trace)},
        ).decode()
        supports_filter = _trace_advertises_filter(trace)

    heads: set[str] = set()
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1].startswith("refs/heads/"):
            heads.add(parts[1].removeprefix("refs/heads/"))
    return heads, supports_filter


def _trace_advertises_filter(trace: Path) -> bool:
    if not trace.is_file():
        return False
    for line in trace.read_text(errors="replace").splitlines():
        _, sep, capability = line.partition("fetch=")
        if sep and "filter" in capability.split():
            return True
    return False


def _git(
    repo: Path,
    *args: str,
    timeout: int = 60,
    stream: bool = False,
    extra_env: dict[str, str] | None = None,
) -> bytes:
    env = {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        "LC_ALL": "C",
    }
    if extra_env:
        env.update(extra_env)
    cmd = ["git", "-C", str(repo), *args]
    # Own session so a timeout kills git *and* its curl/remote-https children.
    # subprocess.run only signals the direct child, which is how one stuck fetch
    # held the whole run.
    proc = subprocess.Popen(  # noqa: S603
        cmd,
        env=env,
        start_new_session=True,
        stdout=None if stream else subprocess.PIPE,
        stderr=None if stream else subprocess.PIPE,
    )
    try:
        stdout, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        raise
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd)
    return stdout or b""


def _du(repo: Path) -> int:
    if not repo.is_dir():
        return 0
    return sum(p.stat().st_size for p in repo.rglob("*") if p.is_file())


def _human(n: int) -> str:
    size = float(max(n, 0))
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{n}B"


if __name__ == "__main__":
    raise SystemExit(main())
