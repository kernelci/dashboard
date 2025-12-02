import hashlib
import time
from datetime import datetime
from typing import Optional, Sequence, TypedDict
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX
from kernelCI_app.helpers.logger import out
from kernelCI_app.management.commands.helpers.aggregation_helpers import simplify_status
from kernelCI_app.models import (
    Builds,
    Checkouts,
    PendingTest,
    ProcessedHardwareStatus,
    SimplifiedStatusChoices,
)


class HardwareStatusRecord(TypedDict):
    """Type definition for hardware status aggregation records."""

    checkout_id: str
    test_origin: str
    platform: str
    compatibles: Optional[list[str]]
    start_time: datetime
    build_pass: int
    build_failed: int
    build_inc: int
    boot_pass: int
    boot_failed: int
    boot_inc: int
    test_pass: int
    test_failed: int
    test_inc: int


def get_hardware_key(
    origin: str, platform: str, checkout_id: str, entity_id: str
) -> bytes:
    """Generate a hash (hardware key) from origin, platform, and checkout ID."""
    return hashlib.sha256(
        f"{origin}|{platform}|{checkout_id}|{entity_id}".encode("utf-8")
    ).digest()


SIMPLIFIED_STATUS_TO_COUNT = {
    SimplifiedStatusChoices.PASS: (1, 0, 0),
    SimplifiedStatusChoices.FAIL: (0, 1, 0),
    SimplifiedStatusChoices.INCONCLUSIVE: (0, 0, 1),
}


def map_simplified_status_to_count(
    status: SimplifiedStatusChoices,
) -> tuple[int, int, int]:
    return SIMPLIFIED_STATUS_TO_COUNT[status]


def _init_status_record(
    checkout: Checkouts,
    test_origin: str,
    platform: str,
    compatibles: Optional[list[str]] = None,
) -> HardwareStatusRecord:
    return {
        "checkout_id": checkout.id,
        "test_origin": test_origin,
        "platform": platform,
        "compatibles": compatibles,
        "start_time": checkout.start_time,
        "build_pass": 0,
        "build_failed": 0,
        "build_inc": 0,
        "boot_pass": 0,
        "boot_failed": 0,
        "boot_inc": 0,
        "test_pass": 0,
        "test_failed": 0,
        "test_inc": 0,
    }


def _collect_test_contexts(
    tests_instances: Sequence[PendingTest],
    builds_by_id: dict[str, Builds],
) -> tuple[list[tuple[PendingTest, Builds, Checkouts, bytes, bytes]], set[bytes]]:
    """Collect valid test contexts with their associated build and checkout."""
    contexts = []
    keys_to_check = set()

    for test in tests_instances:
        try:
            build = builds_by_id[test.build_id]
        except KeyError:
            continue

        checkout: Checkouts = build.checkout

        test_key = get_hardware_key(
            test.origin, test.platform, checkout.id, test.test_id
        )
        build_key = get_hardware_key(test.origin, test.platform, checkout.id, build.id)
        contexts.append((test, build, checkout, test_key, build_key))
        keys_to_check.add(test_key)
        keys_to_check.add(build_key)

    return contexts, keys_to_check


def _get_existing_processed(keys_to_check: set[bytes]) -> set[ProcessedHardwareStatus]:
    """Fetch existing processed entries from the database."""
    return set(ProcessedHardwareStatus.objects.filter(hardware_key__in=keys_to_check))


def _process_test_status(
    test: PendingTest,
    test_h_key: bytes,
    checkout_id: str,
    status_record: HardwareStatusRecord,
    existing_processed: set[ProcessedHardwareStatus],
    new_processed_entries: set[ProcessedHardwareStatus],
) -> bool:
    to_process = ProcessedHardwareStatus(
        hardware_key=test_h_key, checkout_id=checkout_id
    )

    if to_process in existing_processed:
        return False

    t_pass, t_fail, t_inc = map_simplified_status_to_count(test.status)

    if test.is_boot:
        status_record["boot_pass"] += t_pass
        status_record["boot_failed"] += t_fail
        status_record["boot_inc"] += t_inc
    else:
        status_record["test_pass"] += t_pass
        status_record["test_failed"] += t_fail
        status_record["test_inc"] += t_inc

    new_processed_entries.add(to_process)

    return True


def _process_build_status(
    build: Builds,
    build_h_key: bytes,
    status_record: HardwareStatusRecord,
    existing_processed: set[ProcessedHardwareStatus],
    new_processed_entries: set[ProcessedHardwareStatus],
) -> None:
    """Process build status and update status record if not already processed."""

    """
    We can't filter out dummy builds before this step,
    because although we don't count them in build_* status,
    there are tests that are associated with them,
    and those tests are counted in test_* status.
    """
    if build.id.startswith(MAESTRO_DUMMY_BUILD_PREFIX):
        return

    to_process = ProcessedHardwareStatus(
        hardware_key=build_h_key, checkout_id=build.checkout.id
    )

    if to_process in existing_processed:
        return

    if to_process in new_processed_entries:
        return

    b_pass, b_fail, b_inc = map_simplified_status_to_count(
        simplify_status(build.status)
    )
    status_record["build_pass"] += b_pass
    status_record["build_failed"] += b_fail
    status_record["build_inc"] += b_inc

    new_processed_entries.add(to_process)


def aggregate_hardware_status(
    tests_instances: Sequence[PendingTest],
    builds_by_id: dict[str, Builds],
) -> tuple[
    dict[tuple[str, str, str], HardwareStatusRecord], set[ProcessedHardwareStatus]
]:
    """
    Aggregate hardware status from pending tests, builds, and checkouts.
    Returns a dictionary of hardware status records
    keyed by (test_origin, platform, checkout_id)
    and a set of new processed entries.
    """
    hardware_status_data: dict[tuple[str, str, str], HardwareStatusRecord] = {}
    new_processed_entries: set[ProcessedHardwareStatus] = set()

    contexts, keys_to_check = _collect_test_contexts(tests_instances, builds_by_id)

    if not contexts:
        return hardware_status_data, new_processed_entries

    existing_processed = _get_existing_processed(keys_to_check)

    for test, build, checkout, test_h_key, build_h_key in contexts:
        record_key = (test.origin, test.platform, checkout.id)

        try:
            status_record = hardware_status_data[record_key]
        except KeyError:
            status_record = _init_status_record(
                checkout, test.origin, test.platform, test.compatible
            )
            hardware_status_data[record_key] = status_record

        if _process_test_status(
            test,
            test_h_key,
            checkout.id,
            status_record,
            existing_processed,
            new_processed_entries,
        ):
            _process_build_status(
                build,
                build_h_key,
                status_record,
                existing_processed,
                new_processed_entries,
            )

    return hardware_status_data, new_processed_entries


class Command(BaseCommand):
    help = """
        Process pending tests for hardware status aggregation,
        checking corresponding builds and checkouts in the database.
        Pending tests are generated through the monitor_submissions command.
        """

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of pending items to process in one batch",
        )
        parser.add_argument(
            "--loop",
            action="store_true",
            help="Run continuously in a loop",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=1,
            help="Sleep interval in seconds when running in loop mode",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        loop = options["loop"]
        interval = options["interval"]

        if loop:
            out(f"Starting pending aggregation processor (interval={interval}s)...")
            try:
                while True:
                    processed_count = self.process_pending_batch(batch_size)
                    if processed_count == 0:
                        out(f"Sleeping for {interval} seconds")
                        time.sleep(interval)
            except KeyboardInterrupt:
                out("Stopping pending aggregation processor...")
        else:
            self.process_pending_batch(batch_size)

    def process_pending_batch(self, batch_size: int) -> int:
        last_processed_test_id = None

        while True:
            with transaction.atomic():
                out(
                    f"Starting batch processing "
                    f"(last_processed_test_id={str(last_processed_test_id)[:20]}, "
                    f"batch_size={batch_size})..."
                )

                qs = PendingTest.objects.select_for_update(skip_locked=True).order_by(
                    "test_id"
                )
                if last_processed_test_id:
                    qs = qs.filter(test_id__gt=last_processed_test_id)

                pending_test_count = qs[:batch_size].count()

                if not pending_test_count:
                    out("No pending tests found, exiting batch")
                    return 0

                pending_tests_batch = list(qs[:batch_size])
                last_processed_test_id = pending_tests_batch[-1].test_id

                pending_build_ids = {
                    pending_test.build_id for pending_test in pending_tests_batch
                }
                t0 = time.time()
                found_builds = (
                    Builds.objects.select_related("checkout")
                    .only(
                        "id",
                        "status",
                        "checkout__id",
                        "checkout__start_time",
                    )
                    .in_bulk(pending_build_ids)
                )

                if not found_builds:
                    out("No builds found for pending tests, skipping batch")
                    continue

                ready_tests = []
                ready_builds = {}
                skipped_no_build = 0

                for pending_test in pending_tests_batch:
                    build = found_builds.get(pending_test.build_id)
                    if not build:
                        skipped_no_build += 1
                        continue

                    ready_tests.append(pending_test)
                    ready_builds[build.id] = build

                if not ready_tests:
                    continue
                t0 = time.time()
                tests_count = self._process_ready_tests(
                    ready_tests,
                    ready_builds,
                )

                out(
                    f"Batch processed: {tests_count} tests aggregated, "
                    f"skipped (no build): {skipped_no_build}, "
                    f"in {time.time() - t0:.3f}s"
                )

    def _process_ready_tests(
        self,
        ready_tests: Sequence[PendingTest],
        ready_builds: dict[str, Builds],
    ) -> int:
        hardware_status_data, new_processed_entries = aggregate_hardware_status(
            ready_tests, ready_builds
        )

        if hardware_status_data:
            values = [
                (
                    data["checkout_id"],
                    data["test_origin"],
                    data["platform"],
                    data["compatibles"],
                    data["start_time"],
                    data["build_pass"],
                    data["build_failed"],
                    data["build_inc"],
                    data["boot_pass"],
                    data["boot_failed"],
                    data["boot_inc"],
                    data["test_pass"],
                    data["test_failed"],
                    data["test_inc"],
                )
                for data in hardware_status_data.values()
            ]

            t0 = time.time()
            with connection.cursor() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO hardware_status (
                        checkout_id, test_origin, platform, compatibles, start_time,
                        build_pass, build_failed, build_inc,
                        boot_pass, boot_failed, boot_inc,
                        test_pass, test_failed, test_inc
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (test_origin, platform, checkout_id) DO UPDATE SET
                    build_pass = hardware_status.build_pass + EXCLUDED.build_pass,
                    build_failed = hardware_status.build_failed + EXCLUDED.build_failed,
                    build_inc = hardware_status.build_inc + EXCLUDED.build_inc,
                    boot_pass = hardware_status.boot_pass + EXCLUDED.boot_pass,
                    boot_failed = hardware_status.boot_failed + EXCLUDED.boot_failed,
                    boot_inc = hardware_status.boot_inc + EXCLUDED.boot_inc,
                    test_pass = hardware_status.test_pass + EXCLUDED.test_pass,
                    test_failed = hardware_status.test_failed + EXCLUDED.test_failed,
                    test_inc = hardware_status.test_inc + EXCLUDED.test_inc
                    """,
                    values,
                )
            out(
                f"Inserted {len(values)} hardware_status records in {time.time() - t0:.3f}s"
            )

            if new_processed_entries:
                t0 = time.time()
                ProcessedHardwareStatus.objects.bulk_create(
                    new_processed_entries,
                    ignore_conflicts=True,
                )
                out(
                    f"bulk_create processed_hardware_status: n={len(new_processed_entries)} "
                    f"in {time.time() - t0:.3f}s"
                )

        t0 = time.time()
        count = PendingTest.objects.filter(
            test_id__in=[pt.test_id for pt in ready_tests]
        ).delete()[0]
        out(f"Deleted {count} pending tests in {time.time() - t0:.3f}s")

        return count
