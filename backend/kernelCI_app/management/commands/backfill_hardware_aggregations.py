import time
from datetime import timedelta
from typing import Any, Callable, Sequence

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.query import QuerySet
from django.utils import timezone

from kernelCI_app.management.commands.helpers.aggregation_helpers import (
    aggregate_checkouts,
    aggregate_tests,
)
from kernelCI_app.models import (
    Checkouts,
    LatestCheckout,
    PendingTest,
    Tests,
)
from kernelCI_app.helpers.logger import out


class Command(BaseCommand):
    help = """
        Backfill hardware aggregations (LatestCheckout and PendingTest)
        which can later be collected and processed by the process_pending_aggregations command.
    """

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days to look back (default: 30)",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="""Truncate destination tables before backfilling.
                This is a destructive operation and should be used with caution.""",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=2000,
            help="Batch size for processing (default: 2000)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        days = options["days"]
        truncate = options["truncate"]
        batch_size = options["batch_size"]

        cutoff_date = timezone.now() - timedelta(days=days)
        out(f"Backfilling hardware aggregations since {cutoff_date}...")

        if truncate:
            out("Truncating LatestCheckout and PendingTest tables...")
            LatestCheckout.objects.all().delete()
            PendingTest.objects.all().delete()
            out("Truncation complete.")

        out("Backfilling LatestCheckout...")
        checkouts_qs = Checkouts.objects.filter(start_time__gte=cutoff_date).order_by(
            "-start_time"
        )

        # Process checkouts to insert into latest_checkout table
        self.process_queryset(
            checkouts_qs, aggregate_checkouts, batch_size, "Checkouts"
        )

        out("Backfilling PendingTest...")
        tests_qs = (
            Tests.objects.filter(
                start_time__gte=cutoff_date,
                environment_misc__platform__isnull=False,
                build__checkout__id__in=LatestCheckout.objects.values_list(
                    "checkout_id", flat=True
                ),
            )
            .select_related("build")
            .order_by("start_time")
        )

        # Process tests to insert into pending_tests table
        self.process_queryset(tests_qs, aggregate_tests, batch_size, "Tests")

        out("Backfill complete.")

    def process_queryset(
        self,
        queryset: QuerySet[Any],
        aggregator_func: Callable[[Sequence[Any]], None],
        batch_size: int,
        label: str,
    ) -> None:
        """
        Process a queryset in batches using the provided aggregator function

        Iterates through the queryset in chunks, collects items into batches,
        and processes each batch using the aggregator function within a transaction
        """
        count = 0
        total_processed = 0
        batch = []

        t0 = time.time()
        for item in queryset.iterator(chunk_size=batch_size):
            try:
                batch.append(item)
                count += 1
                if count >= batch_size:
                    with transaction.atomic():
                        aggregator_func(batch)
                    total_processed += count
                    out(
                        f"Processed {total_processed} {label} (elapsed time: {time.time() - t0:.2f}s)"
                    )
                    batch = []
                    count = 0
            except Exception as e:
                out(f"Error processing {label}: {e}")
                batch = []
                count = 0
                continue

        if batch:
            aggregator_func(batch)
            total_processed += count
            out(
                f"Processed {total_processed} {label} (elapsed time: {time.time() - t0:.2f}s)"
            )
