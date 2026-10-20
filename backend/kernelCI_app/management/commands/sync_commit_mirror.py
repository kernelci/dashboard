from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from kernelCI_app.helpers.commitSync import (
    DEFAULT_FETCH_TIMEOUT_SECONDS,
    sync_commit_metadata,
)
from kernelCI_app.helpers.logger import log_message, out
from utils.git_mirror_size import record_mirror_size


class Command(BaseCommand):
    help = (
        "Fetch allowlisted git trees into the persistent mirror. "
        "Does not write commits, commit_parents, or synced-tips."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Still fetches into the persistent mirror, so the git repo on "
                "disk is updated. Does not regenerate tree-names.yaml or write "
                "the database."
            ),
        )
        parser.add_argument(
            "--mirror-dir",
            type=str,
            default=None,
            help="Persistent treeless repo path (default: GIT_MIRROR_DIR).",
        )
        parser.add_argument(
            "--fetch-timeout",
            type=int,
            default=DEFAULT_FETCH_TIMEOUT_SECONDS,
            help="Per-remote git fetch timeout in seconds.",
        )
        parser.add_argument(
            "--skip-unfilterable",
            action="store_true",
            help="""Skip servers without partial-clone support instead of taking
                their trees/blobs. Smaller mirror, fewer trees covered.""",
        )
        parser.add_argument(
            "--verbose-git",
            action="store_true",
            help="Let git print its own fetch progress. Noisy; meant for watching a run.",
        )

    def handle(self, *args, **options):
        mirror_dir = Path(options["mirror_dir"] or settings.GIT_MIRROR_DIR)
        try:
            stats = sync_commit_metadata(
                mirror_dir=mirror_dir,
                dry_run=options["dry_run"],
                skip_ingest=True,
                fetch_timeout=options["fetch_timeout"],
                verbose_git=options["verbose_git"],
                skip_unfilterable=options["skip_unfilterable"],
            )
            out(
                "sync_commit_mirror remotes_ok=%(remotes_ok)s remotes_failed=%(remotes_failed)s"
                % stats
            )
        finally:
            self._record_mirror_size(mirror_dir)

    def _record_mirror_size(self, mirror_dir: Path) -> None:
        try:
            size = record_mirror_size(mirror_dir)
        except OSError as exc:
            log_message("sync_commit_mirror failed to record mirror size: %s" % exc)
            return
        if size is None:
            return
        out("sync_commit_mirror mirror_bytes=%s" % size)
