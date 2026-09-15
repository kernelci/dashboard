from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from kernelCI_app.helpers.commitSync import (
    DEFAULT_FETCH_TIMEOUT_SECONDS,
    sync_commit_metadata,
)
from kernelCI_app.helpers.logger import out


class Command(BaseCommand):
    help = (
        "Sync allowlisted git trees into a persistent treeless mirror and upsert "
        "commits / commit_parents. Does not write checkouts.git_commit_message."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Fetch/parse as requested, write nothing to the database or tips file.",
        )
        parser.add_argument(
            "--skip-fetch",
            action="store_true",
            help="Parse objects already in the mirror; do not fetch remotes.",
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
        parser.add_argument(
            "--fetch-timeout",
            type=int,
            default=DEFAULT_FETCH_TIMEOUT_SECONDS,
            help="Per-remote git fetch timeout in seconds.",
        )
        parser.add_argument(
            "--verbose-git",
            action="store_true",
            help="Let git print its own fetch progress. Noisy; meant for watching a run.",
        )

    def handle(self, *args, **options):
        mirror_dir = options["mirror_dir"] or settings.GIT_MIRROR_DIR
        stats = sync_commit_metadata(
            mirror_dir=Path(mirror_dir),
            dry_run=options["dry_run"],
            skip_fetch=options["skip_fetch"],
            fill_gaps=options["fill_gaps"],
            fetch_timeout=options["fetch_timeout"],
            verbose_git=options["verbose_git"],
        )
        out(
            "sync_commits remotes_ok=%(remotes_ok)s remotes_failed=%(remotes_failed)s "
            "parsed=%(parsed)s commits_written=%(commits_written)s "
            "edges_written=%(edges_written)s gaps_fetched=%(gaps_fetched)s "
            "gaps_written=%(gaps_written)s" % stats
        )
