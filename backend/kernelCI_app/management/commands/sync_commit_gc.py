from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from kernelCI_app.helpers.commitSync import gc_mirror
from kernelCI_app.helpers.logger import log_message, out
from utils.git_mirror_size import record_mirror_size


class Command(BaseCommand):
    help = (
        "Delete unreachable mirror objects now and repack what remains. "
        "Bitmap indexes stay off so a treeless pack can be rewritten."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--mirror-dir",
            type=str,
            default=None,
            help="Persistent treeless repo path (default: GIT_MIRROR_DIR).",
        )

    def handle(self, *args, **options):
        mirror_dir = Path(options["mirror_dir"] or settings.GIT_MIRROR_DIR)
        gc_mirror(mirror_dir)
        self._record_mirror_size(mirror_dir)

    def _record_mirror_size(self, mirror_dir: Path) -> None:
        try:
            size = record_mirror_size(mirror_dir)
        except OSError as exc:
            log_message("sync_commit_gc failed to record mirror size: %s" % exc)
            return
        if size is None:
            return
        out("sync_commit_gc mirror_bytes=%s" % size)
