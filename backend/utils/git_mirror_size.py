"""On-disk size of the commit-metadata git mirror.

sync_commit_mirror writes one integer at the end of a run. The long-lived
metrics process reads that file; the cron must not publish a gauge itself.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector

SIZE_FILENAME = "mirror-size-bytes"
DEFAULT_MIRROR_DIR = "/var/lib/kernelci/git-mirror"


def directory_size_bytes(path: Path) -> int:
    """Apparent size of files under path. Missing path is 0.

    A file that vanishes mid-walk is skipped. A directory that cannot be
    listed raises, so the caller can keep the previous size file.
    """
    root = Path(path)
    if not root.is_dir():
        return 0

    total = 0

    def onerror(err: OSError) -> None:
        raise err

    for dirpath, _, filenames in os.walk(root, onerror=onerror):
        for name in filenames:
            file_path = Path(dirpath) / name
            try:
                total += file_path.stat(follow_symlinks=False).st_size
            except OSError:
                continue
    return total


def record_mirror_size(repo_dir: Path) -> int | None:
    """Write repo_dir/mirror-size-bytes. None if there is no directory to measure.

    The write is atomic: temp file in the same directory, fsync, then replace.
    A listing error leaves the previous file in place.
    """
    root = Path(repo_dir)
    if not root.is_dir():
        return None
    size = directory_size_bytes(root)
    _atomic_write(root / SIZE_FILENAME, f"{size}\n".encode())
    return size


def _atomic_write(path: Path, payload: bytes) -> None:
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    tmp = Path(tmp_name)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
    except BaseException:
        os.close(fd)
        tmp.unlink(missing_ok=True)
        raise
    os.close(fd)
    try:
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


class MirrorSizeCollector(Collector):
    """Expose the size file written by sync_commit_mirror. Absent file emits nothing."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def collect(self):
        try:
            st = self.path.stat()
            size = int(self.path.read_text().strip())
        except (OSError, ValueError):
            return
        yield GaugeMetricFamily(
            "git_mirror_size_bytes",
            "Apparent size in bytes of the git mirror after the last sync_commit_mirror run",
            value=size,
        )
        yield GaugeMetricFamily(
            "git_mirror_size_mtime_seconds",
            "Unix mtime of the git mirror size file, set when sync_commit_mirror finishes",
            value=st.st_mtime,
        )
