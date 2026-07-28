"""
Management command to delete unused entries from the hardware status tables.

Removes hardware build/test status and processed listing entries that have no
corresponding checkout_id in the LatestCheckout table.
"""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from kernelCI_app.management.commands.helpers.healthcheck import (
    MONITORING_ID_PARAM_HELP_TEXT,
    run_with_healthcheck_monitoring,
)
from kernelCI_app.models import (
    HardwareBuildStatus,
    HardwareTestStatus,
    LatestCheckout,
    ProcessedListingItems,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Delete hardware status entries with no corresponding checkout_id "
        "in the LatestCheckout table"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10000,
            help="Number of records to delete per batch (default: 10000)",
        )
        parser.add_argument(
            "--monitoring-id",
            type=str,
            default=None,
            help=MONITORING_ID_PARAM_HELP_TEXT,
        )

    def handle(self, *args, **options):
        monitoring_id = options.get("monitoring_id")
        return run_with_healthcheck_monitoring(
            monitoring_id=monitoring_id,
            action=lambda: self._run_action(options),
        )

    # Each table is pruned by the field its delete batches are keyed on
    ORPHAN_TARGETS = (
        (HardwareBuildStatus, "checkout_id"),
        (HardwareTestStatus, "checkout_id"),
        (ProcessedListingItems, "listing_item_key"),
    )

    def _delete_orphans(
        self, *, model, batch_field: str, valid_checkout_ids: set[str], batch_size: int
    ) -> int:
        table = model._meta.db_table
        orphans = model.objects.exclude(checkout_id__in=valid_checkout_ids).values_list(
            batch_field, flat=True
        )
        total = orphans.count()
        if total == 0:
            return 0

        deleted = 0
        while True:
            batch = list(orphans[:batch_size])
            if not batch:
                break
            deleted += model.objects.filter(**{f"{batch_field}__in": batch}).delete()[0]
            self.stdout.write(f"Deleted {table} entries (total: {deleted}/{total})")

        return deleted

    def _run_action(self, options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        with transaction.atomic():
            valid_checkout_ids = set(
                LatestCheckout.objects.values_list("checkout_id", flat=True)
            )

            if dry_run:
                counts = {
                    model._meta.db_table: model.objects.exclude(
                        checkout_id__in=valid_checkout_ids
                    ).count()
                    for model, _ in self.ORPHAN_TARGETS
                }
                summary = ", ".join(f"{table}={n}" for table, n in counts.items())
                self.stdout.write(
                    self.style.WARNING(
                        f"[DRY RUN] Would delete {summary}. "
                        "Run without --dry-run to execute deletion."
                    )
                )
                return

            deleted = {
                model._meta.db_table: self._delete_orphans(
                    model=model,
                    batch_field=batch_field,
                    valid_checkout_ids=valid_checkout_ids,
                    batch_size=batch_size,
                )
                for model, batch_field in self.ORPHAN_TARGETS
            }

        summary = ", ".join(f"{table}={n}" for table, n in deleted.items())
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {summary}."))
