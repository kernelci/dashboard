"""
Management command to delete unused entries from hardware_status table.

Removes HardwareStatus entries that have no corresponding checkout_id in the LatestCheckout table.
"""

import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from kernelCI_app.models import HardwareStatus, LatestCheckout, ProcessedHardwareStatus

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Delete HardwareStatus entries with no corresponding checkout_id "
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

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        with transaction.atomic():
            valid_checkout_ids = set(
                LatestCheckout.objects.values_list("checkout_id", flat=True)
            )

            orphaned_hardware_entries = HardwareStatus.objects.exclude(
                checkout_id__in=valid_checkout_ids
            ).values_list("checkout_id", flat=True)
            orphaned_hardware_count = orphaned_hardware_entries.count()

            orphaned_processed_hardware_entries = (
                ProcessedHardwareStatus.objects.exclude(
                    checkout_id__in=valid_checkout_ids
                )
            ).values_list("hardware_key", flat=True)

            orphaned_processed_hardware_count = (
                orphaned_processed_hardware_entries.count()
            )

            if orphaned_hardware_count == 0 and orphaned_processed_hardware_count == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        "No orphaned HardwareStatus/ProcessedHardwareStatus entries found."
                    )
                )
                return

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"[DRY RUN] Would delete {orphaned_hardware_count} HardwareStatus entries and "
                        f"{orphaned_processed_hardware_count} ProcessedHardwareStatus entries "
                        "Run without --dry-run to execute deletion."
                    )
                )
                return

            self.stdout.write(
                f"Found {orphaned_hardware_count} HardwareStatus entries "
                f"and {orphaned_processed_hardware_count} ProcessedHardwareStatus entries "
                "with no corresponding LatestCheckout."
            )

            total_hardware_deleted = 0
            total_processed_hardware_deleted = 0
            while True:
                hardware_batch_ids = list(orphaned_hardware_entries[:batch_size])
                processed_hardware_batch_ids = list(
                    orphaned_processed_hardware_entries[:batch_size]
                )

                if not hardware_batch_ids and not processed_hardware_batch_ids:
                    break

                if hardware_batch_ids:
                    hardware_delete_count = HardwareStatus.objects.filter(
                        checkout_id__in=hardware_batch_ids
                    ).delete()[0]
                    self.stdout.write(
                        f"Deleted hardware_status(n={hardware_delete_count}) entries "
                        f"(total: {total_hardware_deleted}/{orphaned_hardware_count})"
                    )
                    total_hardware_deleted += hardware_delete_count

                if processed_hardware_batch_ids:
                    processed_hardware_delete_count = (
                        ProcessedHardwareStatus.objects.filter(
                            hardware_key__in=processed_hardware_batch_ids
                        ).delete()[0]
                    )

                    total_processed_hardware_deleted += processed_hardware_delete_count

                    self.stdout.write(
                        f"Deleted processed_hardware_status(n={processed_hardware_delete_count}) entries "
                        f"(total: {total_processed_hardware_deleted}/{orphaned_processed_hardware_count})"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted hardware_status(n={total_hardware_deleted}) "
                f"and processed_hardware_status(n={total_processed_hardware_deleted})."
            )
        )
