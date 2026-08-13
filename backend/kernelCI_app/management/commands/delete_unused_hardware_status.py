"""
Prune HardwareStatus and ProcessedListingItems older than
HARDWARE_STATUS_RETENTION_DAYS. Both use the same cutoff so already-processed
entries stay in sync with status rows and we avoid over/undercounting on
re-ingest.
"""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from kernelCI_app.management.commands.helpers.healthcheck import (
    MONITORING_ID_PARAM_HELP_TEXT,
    run_with_healthcheck_monitoring,
)
from kernelCI_app.models import Checkouts, HardwareStatus, ProcessedListingItems


class Command(BaseCommand):
    help = (
        "Delete HardwareStatus entries (and their ProcessedListingItems) older "
        "than HARDWARE_STATUS_RETENTION_DAYS"
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

    def _run_action(self, options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        cutoff = timezone.now() - timedelta(
            days=settings.HARDWARE_STATUS_RETENTION_DAYS
        )

        stale_hardware = HardwareStatus.objects.filter(start_time__lt=cutoff)
        recent_checkout_ids = Checkouts.objects.filter(start_time__gte=cutoff).values(
            "id"
        )
        stale_processed = ProcessedListingItems.objects.exclude(
            checkout_id__in=recent_checkout_ids
        )

        stale_hardware_count = stale_hardware.count()
        stale_processed_count = stale_processed.count()

        if stale_hardware_count == 0 and stale_processed_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "No orphaned HardwareStatus/ProcessedListingItems entries found."
                )
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Would delete {stale_hardware_count} HardwareStatus entries and "
                    f"{stale_processed_count} ProcessedListingItems entries "
                    "Run without --dry-run to execute deletion."
                )
            )
            return

        self.stdout.write(
            f"Found {stale_hardware_count} HardwareStatus entries "
            f"and {stale_processed_count} ProcessedListingItems entries "
            f"older than {settings.HARDWARE_STATUS_RETENTION_DAYS} days."
        )

        total_hardware_deleted = 0
        total_processed_deleted = 0
        with transaction.atomic():
            while True:
                hardware_batch = list(
                    stale_hardware.values_list(
                        "test_origin", "platform", "checkout_id"
                    )[:batch_size]
                )
                processed_batch = list(
                    stale_processed.values_list("listing_item_key", flat=True)[
                        :batch_size
                    ]
                )

                if not hardware_batch and not processed_batch:
                    break

                if hardware_batch:
                    hardware_delete_count = HardwareStatus.objects.filter(
                        pk__in=hardware_batch
                    ).delete()[0]
                    total_hardware_deleted += hardware_delete_count
                    self.stdout.write(
                        f"Deleted hardware_status(n={hardware_delete_count}) entries "
                        f"(total: {total_hardware_deleted}/{stale_hardware_count})"
                    )

                if processed_batch:
                    processed_delete_count = ProcessedListingItems.objects.filter(
                        listing_item_key__in=processed_batch
                    ).delete()[0]
                    total_processed_deleted += processed_delete_count
                    self.stdout.write(
                        f"Deleted processed_listing_items(n={processed_delete_count}) entries "
                        f"(total: {total_processed_deleted}/{stale_processed_count})"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted hardware_status(n={total_hardware_deleted}) "
                f"and processed_listing_items(n={total_processed_deleted})."
            )
        )
