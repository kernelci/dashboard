"""
Prune HardwareStatus rows older than HARDWARE_STATUS_RETENTION_DAYS.

ProcessedListingItems is shared with tree listing and rollup; we do not prune
it here to avoid re-ingest double-counting on those features.
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
from kernelCI_app.models import HardwareStatus


class Command(BaseCommand):
    help = "Delete HardwareStatus entries older than HARDWARE_STATUS_RETENTION_DAYS"

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
        stale_hardware_count = stale_hardware.count()

        if stale_hardware_count == 0:
            self.stdout.write(
                self.style.SUCCESS("No stale HardwareStatus entries found.")
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Would delete {stale_hardware_count} HardwareStatus entries. "
                    "Run without --dry-run to execute deletion."
                )
            )
            return

        self.stdout.write(
            f"Found {stale_hardware_count} HardwareStatus entries "
            f"older than {settings.HARDWARE_STATUS_RETENTION_DAYS} days."
        )

        total_hardware_deleted = 0
        while True:
            hardware_batch = list(
                stale_hardware.values_list("test_origin", "platform", "checkout_id")[
                    :batch_size
                ]
            )

            if not hardware_batch:
                break

            with transaction.atomic():
                hardware_delete_count = HardwareStatus.objects.filter(
                    pk__in=hardware_batch
                ).delete()[0]
                total_hardware_deleted += hardware_delete_count
                self.stdout.write(
                    f"Deleted hardware_status(n={hardware_delete_count}) entries "
                    f"(total: {total_hardware_deleted}/{stale_hardware_count})"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted hardware_status(n={total_hardware_deleted})."
            )
        )
