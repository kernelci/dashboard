from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from kernelCI_app.helpers.commitSync import sync_commit_metadata
from kernelCI_app.helpers.logger import out


class Command(BaseCommand):
    help = (
        "Upsert commits / commit_parents from objects already in the persistent "
        "mirror (tip delta). Does not write checkouts.git_commit_message."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse as requested, write nothing to the database or tips file.",
        )
        parser.add_argument(
            "--fill-gaps",
            action="store_true",
            help="One-shot SHA fetch for checkout hashes still missing from commits.",
        )
        parser.add_argument(
            "--mirror-dir",
            type=str,
            default=None,
            help="Persistent treeless repo path (default: GIT_MIRROR_DIR).",
        )

    def handle(self, *args, **options):
        mirror_dir = options["mirror_dir"] or settings.GIT_MIRROR_DIR
        stats = sync_commit_metadata(
            mirror_dir=Path(mirror_dir),
            dry_run=options["dry_run"],
            skip_fetch=True,
            fill_gaps=options["fill_gaps"],
        )
        out(
            "sync_commit_ingest parsed=%(parsed)s commits_written=%(commits_written)s "
            "edges_written=%(edges_written)s gaps_fetched=%(gaps_fetched)s "
            "gaps_written=%(gaps_written)s" % stats
        )
