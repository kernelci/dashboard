import hashlib
import signal
import time
from datetime import datetime
from typing import Literal, Optional, Sequence, TypedDict, Union
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX
from kernelCI_app.helpers.logger import out
from kernelCI_app.management.commands.helpers.aggregation_helpers import simplify_status
from kernelCI_app.models import (
    Builds,
    Checkouts,
    PendingTest,
    PendingBuilds,
    ProcessedListingItems,
    SimplifiedStatusChoices,
)


class ListingItemCount(TypedDict):
    build_pass: int
    build_failed: int
    build_inc: int
    boot_pass: int
    boot_failed: int
    boot_inc: int
    test_pass: int
    test_failed: int
    test_inc: int


class TreeListingRecord(ListingItemCount):
    checkout_id: str
    origin: str
    tree_name: str | None
    git_repository_url: str | None
    git_repository_branch: str | None
    git_commit_hash: str | None
    git_commit_name: str | None
    git_commit_tags: list[str] | None
    start_time: datetime | None


class HardwareStatusRecord(ListingItemCount):
    checkout_id: str
    test_origin: str
    platform: str
    compatibles: Optional[list[str]]
    start_time: datetime


def get_hardware_key(
    origin: str, platform: str, checkout_id: str, entity_id: str
) -> bytes:
    """Generate a hash (hardware key) from origin, platform, and checkout ID."""
    return hashlib.sha256(
        f"{origin}|{platform}|{checkout_id}|{entity_id}".encode("utf-8")
    ).digest()


def get_tree_listing_key(
    *, origin: str, tree_name: str, git_url: str, git_branch: str, entity_id: str
) -> bytes:
    """Generate a hash (tree listing key) from parameters."""
    return hashlib.sha256(
        f"{origin}|{tree_name}|{git_url}|{git_branch}|{entity_id}".encode("utf-8")
    ).digest()


SIMPLIFIED_STATUS_TO_COUNT = {
    SimplifiedStatusChoices.PASS: (1, 0, 0),
    SimplifiedStatusChoices.FAIL: (0, 1, 0),
    SimplifiedStatusChoices.INCONCLUSIVE: (0, 0, 1),
    None: (0, 0, 1),
}


def map_simplified_status_to_count(
    status: SimplifiedStatusChoices,
) -> tuple[int, int, int]:
    return SIMPLIFIED_STATUS_TO_COUNT[status]


def _init_tree_listing_record(*, checkout: Checkouts) -> TreeListingRecord:
    return {
        "checkout_id": checkout.id,
        "origin": checkout.origin,
        "tree_name": checkout.tree_name,
        "git_repository_url": checkout.git_repository_url,
        "git_repository_branch": checkout.git_repository_branch,
        "git_commit_hash": checkout.git_commit_hash,
        "git_commit_name": checkout.git_commit_name,
        "git_commit_tags": checkout.git_commit_tags,
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


def _init_hardware_status_record(
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


def _collect_hardware_status_contexts(
    tests_instances: Sequence[PendingTest],
    builds_by_id: dict[str, Builds],
) -> tuple[list[tuple[PendingTest, Builds, Checkouts, bytes, bytes]], set[bytes]]:
    """Collect valid test contexts with their associated build and checkout."""
    contexts = []
    keys_to_check = set()

    for test in tests_instances:
        # Hardware status only counts tests with non-null platform
        if test.platform is None:
            continue

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


def _get_existing_processed(keys_to_check: set[bytes]) -> set[ProcessedListingItems]:
    """Fetch existing processed entries from the database."""
    return set(ProcessedListingItems.objects.filter(listing_item_key__in=keys_to_check))


def _check_item_was_processed(
    *,
    existing_processed: set[ProcessedListingItems],
    new_processed_entries: set[ProcessedListingItems],
    status_record: ListingItemCount,
    listing_item_key: bytes,
    item_checkout_id: str,
    item_status: Optional[SimplifiedStatusChoices],
    decrement_status_type: Literal["build_inc", "boot_inc", "test_inc"],
) -> bool:
    """
    Checks if an item is already processed in existing or new processed entries.
    Returns True if already processed, False otherwise.

    Item means either PendingTest or Builds/PendingBuilds.
    """
    for existing in existing_processed:
        if (
            existing.listing_item_key == listing_item_key
            and existing.checkout_id == item_checkout_id
        ):
            if existing.status is not None:
                return True
            if existing.status is None and item_status is None:
                return True
            # If existing status is null and new status is not null,
            # we will update this entry as well as the count
            status_record[decrement_status_type] -= 1
            break

    for new_entry in new_processed_entries:
        if (
            new_entry.listing_item_key == listing_item_key
            and new_entry.checkout_id == item_checkout_id
        ):
            if new_entry.status is not None:
                return True
            if new_entry.status is None and item_status is None:
                return True
            # It can happen to exist both in existing_processed and new_processed_entries
            # in which case we do double the decrement, because both previous entries incremented it
            status_record[decrement_status_type] -= 1
            new_processed_entries.remove(
                new_entry
            )  # no need to process the old entry anymore
            break

    return False


def _process_test_status(
    test: PendingTest,
    test_listing_key: bytes,
    checkout_id: str,
    status_record: ListingItemCount,
    existing_processed: set[ProcessedListingItems],
    new_processed_entries: set[ProcessedListingItems],
) -> bool:
    """
    Checks if test is already processed, if not,
    updates status record and marks it as processed.
    """
    # TODO: we should be checking if it is already processed before entering this function
    to_process = ProcessedListingItems(
        listing_item_key=test_listing_key, checkout_id=checkout_id, status=test.status
    )

    if _check_item_was_processed(
        existing_processed=existing_processed,
        new_processed_entries=new_processed_entries,
        status_record=status_record,
        listing_item_key=test_listing_key,
        item_checkout_id=checkout_id,
        item_status=test.status,
        decrement_status_type="boot_inc" if test.is_boot else "test_inc",
    ):
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
    build_id: str,
    build_checkout_id: str,
    build_status: Optional[SimplifiedStatusChoices],
    build_listing_key: bytes,
    status_record: ListingItemCount,
    existing_processed: set[ProcessedListingItems],
    new_processed_entries: set[ProcessedListingItems],
) -> None:
    """Process build status and update status record if not already processed."""

    # We can't remove those builds earlier because
    # we don't count dummy builds, but there are tests
    # associated with them and those tests are counted.
    if build_id.startswith(MAESTRO_DUMMY_BUILD_PREFIX):
        return

    to_process = ProcessedListingItems(
        listing_item_key=build_listing_key,
        checkout_id=build_checkout_id,
        status=build_status,
    )

    if _check_item_was_processed(
        existing_processed=existing_processed,
        new_processed_entries=new_processed_entries,
        status_record=status_record,
        listing_item_key=build_listing_key,
        item_checkout_id=build_checkout_id,
        item_status=build_status,
        decrement_status_type="build_inc",
    ):
        return

    b_pass, b_fail, b_inc = map_simplified_status_to_count(build_status)

    status_record["build_pass"] += b_pass
    status_record["build_failed"] += b_fail
    status_record["build_inc"] += b_inc

    new_processed_entries.add(to_process)


def _collect_tree_listing_contexts(
    ready_tests: Sequence[PendingTest],
    test_builds_by_id: dict[str, Builds],
    ready_builds: Sequence[PendingBuilds],
    build_checkouts_by_id: dict[str, Checkouts],
) -> tuple[
    list[tuple[Union[PendingTest, PendingBuilds], Checkouts, bytes]], set[bytes]
]:
    """
    Creates the contexts for all treeListing items,
    combining the test/build, their respective checkout, and hash key
    into a single list.
    Since we are working with tests and builds independently, they are combined into a single field.

    Also returns the set of all keys to check in the ProcessedListingItems table.
    """
    keys_to_check: set[bytes] = set()
    contexts: list[tuple[Union[PendingTest, Builds], Checkouts, bytes]] = []

    for test in ready_tests:
        test_id = test.test_id
        try:
            test_checkout = test_builds_by_id[test.build_id].checkout
        except KeyError:
            continue

        test_key = get_tree_listing_key(
            origin=test_checkout.origin,
            tree_name=test_checkout.tree_name,
            git_url=test_checkout.git_repository_url,
            git_branch=test_checkout.git_repository_branch,
            entity_id=test_id,
        )
        keys_to_check.add(test_key)
        contexts.append((test, test_checkout, test_key))

    for build in ready_builds:
        build_id = build.build_id
        try:
            build_checkout = build_checkouts_by_id[build_id]
        except KeyError:
            continue

        build_key = get_tree_listing_key(
            origin=build_checkout.origin,
            tree_name=build_checkout.tree_name,
            git_url=build_checkout.git_repository_url,
            git_branch=build_checkout.git_repository_branch,
            entity_id=build_id,
        )
        keys_to_check.add(build_key)
        contexts.append((build, build_checkout, build_key))

    return contexts, keys_to_check


def aggregate_tree_listing(
    ready_tests: Sequence[PendingTest],
    test_builds_by_id: dict[str, Builds],
    ready_builds: Sequence[PendingBuilds],
    build_checkouts_by_id: dict[str, Checkouts],
) -> tuple[dict[str, TreeListingRecord], set[ProcessedListingItems]]:
    """
    Prepares tree_listing data from pending tests and builds.

    Returns a dictionary of treeListing records
    keyed by checkout_id (for updating TreeListing table)
    and a set of new processed entries (for updating the ProcessedListingItems table).
    """
    if not ready_tests and not ready_builds:
        return {}, set()

    tree_listing_data: dict[str, TreeListingRecord] = {}
    new_processed_entries: set[ProcessedListingItems] = set()

    contexts, keys_to_check = _collect_tree_listing_contexts(
        ready_tests,
        test_builds_by_id,
        ready_builds,
        build_checkouts_by_id,
    )

    if not contexts:
        return {}, set()

    existing_processed = _get_existing_processed(keys_to_check)

    for item, checkout, listing_key in contexts:
        checkout_id = checkout.id
        try:
            status_record = tree_listing_data[checkout_id]
        except KeyError:
            status_record = _init_tree_listing_record(checkout=checkout)
            tree_listing_data[checkout_id] = status_record

        if isinstance(item, PendingTest):
            _process_test_status(
                test=item,
                test_listing_key=listing_key,
                checkout_id=checkout_id,
                status_record=status_record,
                existing_processed=existing_processed,
                new_processed_entries=new_processed_entries,
            )
        elif isinstance(item, PendingBuilds):
            _process_build_status(
                build_id=item.build_id,
                build_checkout_id=checkout_id,
                build_status=item.status,
                build_listing_key=listing_key,
                status_record=status_record,
                existing_processed=existing_processed,
                new_processed_entries=new_processed_entries,
            )

    return tree_listing_data, new_processed_entries


def aggregate_hardware_status(
    tests_instances: Sequence[PendingTest],
    test_builds_by_id: dict[str, Builds],
) -> tuple[
    dict[tuple[str, str, str], HardwareStatusRecord], set[ProcessedListingItems]
]:
    """
    Aggregate hardware status from pending tests, builds, and checkouts.

    Returns a dictionary of hardware status records
    keyed by `(test_origin, platform, checkout_id)` (for updating HardwareStatus table)
    and a set of new processed entries (for updating the ProcessedListingItems table).

    This function does not update the database, only prepares the data for it.
    """
    hardware_status_data: dict[tuple[str, str, str], HardwareStatusRecord] = {}
    new_processed_entries: set[ProcessedListingItems] = set()

    contexts, keys_to_check = _collect_hardware_status_contexts(
        tests_instances, test_builds_by_id
    )

    if not contexts:
        return hardware_status_data, new_processed_entries

    existing_processed = _get_existing_processed(keys_to_check)

    for test, build, checkout, test_h_key, build_h_key in contexts:
        record_key = (test.origin, test.platform, checkout.id)

        try:
            status_record = hardware_status_data[record_key]
        except KeyError:
            status_record = _init_hardware_status_record(
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
                build_id=build.id,
                build_checkout_id=checkout.id,
                build_status=simplify_status(build.status),
                build_listing_key=build_h_key,
                status_record=status_record,
                existing_processed=existing_processed,
                new_processed_entries=new_processed_entries,
            )

    return hardware_status_data, new_processed_entries


class Command(BaseCommand):
    help = """
        Process pending tests for hardware status aggregation,
        checking corresponding builds and checkouts in the database.
        Pending tests are generated through the monitor_submissions command.
        """
    running = True

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        out(f"Received signal {signum}, initiating graceful shutdown...")
        raise SystemExit(0)

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
            signal.signal(signal.SIGTERM, self.signal_handler)
            signal.signal(signal.SIGINT, self.signal_handler)

            out(f"Starting pending aggregation processor (interval={interval}s)...")
            try:
                while self.running:
                    processed_count = self.process_pending_batch(batch_size)
                    if processed_count == 0:
                        out(f"Sleeping for {interval} seconds")
                        time.sleep(interval)
            except KeyboardInterrupt:
                out("Stopping pending aggregation processor...")
            finally:
                out("Pending aggregation processor shutdown complete")
        else:
            self.process_pending_batch(batch_size)

    def _delete_ready_builds(self, *, ready_builds: Sequence[PendingBuilds]) -> int:
        """
        Deletes PendingBuilds that have been processed.
        Returns the number of deleted entries.
        """

        if not ready_builds:
            return 0

        t0 = time.time()
        count = PendingBuilds.objects.filter(
            build_id__in=[build.build_id for build in ready_builds]
        ).delete()[0]
        out(f"Deleted {count} pending builds in {time.time() - t0:.3f}s")

        return count

    def _delete_ready_tests(self, *, ready_tests: Sequence[PendingTest]) -> int:
        """
        Deletes PendingTests that have been processed.
        Returns the number of deleted entries.
        """

        if not ready_tests:
            return 0

        t0 = time.time()
        count = PendingTest.objects.filter(
            test_id__in=[test.test_id for test in ready_tests]
        ).delete()[0]
        out(f"Deleted {count} pending tests in {time.time() - t0:.3f}s")

        return count

    def _process_new_processed_entries(
        self, new_processed_entries: set[ProcessedListingItems]
    ) -> None:
        if not new_processed_entries:
            return

        t0 = time.time()
        ProcessedListingItems.objects.bulk_create(
            new_processed_entries,
            update_conflicts=True,
            update_fields=["checkout_id", "status"],
            unique_fields=["listing_item_key"],
        )
        out(
            f"bulk_create ProcessedListingItems: n={len(new_processed_entries)} "
            f"in {time.time() - t0:.3f}s"
        )

    def _process_tree_listing(
        self,
        tree_listing_data: dict[str, TreeListingRecord],
    ) -> None:
        if not tree_listing_data:
            return

        values = [
            (
                data["build_pass"],
                data["build_failed"],
                data["build_inc"],
                data["boot_pass"],
                data["boot_failed"],
                data["boot_inc"],
                data["test_pass"],
                data["test_failed"],
                data["test_inc"],
                data["origin"],
                data["tree_name"],
                data["git_repository_branch"],
                data["git_repository_url"],
                data["git_commit_hash"],
            )
            for data in tree_listing_data.values()
        ]

        t0 = time.time()
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                UPDATE tree_listing
                SET
                    build_pass = tree_listing.build_pass + %s,
                    build_failed = tree_listing.build_failed + %s,
                    build_inc = tree_listing.build_inc + %s,
                    boot_pass = tree_listing.boot_pass + %s,
                    boot_failed = tree_listing.boot_failed + %s,
                    boot_inc = tree_listing.boot_inc + %s,
                    test_pass = tree_listing.test_pass + %s,
                    test_failed = tree_listing.test_failed + %s,
                    test_inc = tree_listing.test_inc + %s
                WHERE
                    -- IS NOT DISTINCT FROM used to treat NULLs as equal
                    tree_listing.origin = %s
                    AND tree_listing.tree_name IS NOT DISTINCT FROM %s
                    AND tree_listing.git_repository_branch IS NOT DISTINCT FROM %s
                    AND tree_listing.git_repository_url IS NOT DISTINCT FROM %s
                    AND tree_listing.git_commit_hash IS NOT DISTINCT FROM %s
                """,
                values,
            )

        out(f"Inserted {len(values)} tree_listing records in {time.time() - t0:.3f}s")

    def _process_hardware_status(
        self,
        hardware_status_data: dict[tuple[str, str, str], HardwareStatusRecord],
    ) -> None:
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

    def _get_ready_builds(
        self, *, last_processed_build_id: Optional[str], batch_size: int
    ) -> tuple[Sequence[PendingBuilds], dict[str, Checkouts], Optional[str], int, int]:
        """
        Fetches a batch of pending builds along with their associated build and checkout information.
        Args:
            last_processed_build_id (Optional[str]): The ID of the last processed build from a
                previous batch. If provided, only builds with IDs greater than this will be fetched.
                Used for pagination across batches.
            batch_size (int): The maximum number of pending builds to fetch in this batch.
        Returns a tuple containing:
            - list[PendingBuild]: List of pending builds ready for processing.
            - Optional[str]: The updated last_processed_build_id.
            - int: Count of pending builds that were skipped because their checkout wasn't found.
            - int: The count of pending builds that were found.
        Note:
            - Returns ([], last_processed_build_id, skipped_count, pending_build_count)
              if there are no pending builds, if no checkouts are found
              for the pending builds or if there are no ready_builds.
        """

        ready_builds: Sequence[PendingBuilds] = []
        build_checkouts_by_id: dict[str, Checkouts] = {}
        skipped_no_checkout = 0
        pending_build_count = 0

        qs = PendingBuilds.objects.select_for_update(skip_locked=True).order_by(
            "build_id"
        )
        if last_processed_build_id:
            qs = qs.filter(build_id__gt=last_processed_build_id)

        pending_builds_batch = list(qs[:batch_size])
        pending_build_count = len(pending_builds_batch)

        if pending_build_count == 0:
            out("No pending builds found, exiting batch")
            return (
                ready_builds,
                build_checkouts_by_id,
                last_processed_build_id,
                skipped_no_checkout,
                pending_build_count,
            )

        last_processed_build_id = pending_builds_batch[-1].build_id

        pending_build_checkout_ids = {
            pending_build.checkout_id for pending_build in pending_builds_batch
        }
        found_checkouts = Checkouts.objects.only(
            "id",
            "start_time",
        ).in_bulk(pending_build_checkout_ids)

        if not found_checkouts:
            out("No checkouts found for pending builds, skipping batch")
            return (
                ready_builds,
                build_checkouts_by_id,
                last_processed_build_id,
                skipped_no_checkout,
                pending_build_count,
            )

        for pending_build in pending_builds_batch:
            checkout = found_checkouts.get(pending_build.checkout_id)
            if not checkout:
                skipped_no_checkout += 1
                continue
            ready_builds.append(pending_build)
            build_checkouts_by_id[pending_build.build_id] = checkout

        return (
            ready_builds,
            build_checkouts_by_id,
            last_processed_build_id,
            skipped_no_checkout,
            pending_build_count,
        )

    def _get_ready_tests(
        self, *, last_processed_test_id: Optional[str], batch_size: int
    ) -> tuple[Sequence[PendingTest], dict[str, Builds], Optional[str], int, int]:
        """
        Fetches a batch of pending tests along with their associated build and checkout information.
        Args:
            last_processed_test_id (Optional[str]): The ID of the last processed test from a
                previous batch. If provided, only tests with IDs greater than this will be fetched.
                Used for pagination across batches.
            batch_size (int): The maximum number of pending tests to fetch in this batch.
        Returns a tuple containing:
            - list[PendingTest]: List of pending tests and related data ready for processing.
            - dict[str, Builds]: Dictionary mapping build IDs to their corresponding Build objects.
            - Optional[str]: The updated last_processed_test_id.
            - int: Count of pending tests that were skipped because their build wasn't found.
            - int: The count of pending tests that were found.
        Note:
            - Returns ([], {}, last_processed_test_id, skipped_count, pending_test_count)
              if there are no pending tests, if no builds are found
              for the pending tests or if there are no ready_tests.
        """
        ready_tests: Sequence[PendingTest] = []
        test_builds_by_id: dict[str, Builds] = {}
        skipped_no_build = 0
        pending_test_count = 0

        qs = PendingTest.objects.select_for_update(skip_locked=True).order_by("test_id")
        if last_processed_test_id:
            qs = qs.filter(test_id__gt=last_processed_test_id)

        pending_tests_batch = list(qs[:batch_size])
        pending_test_count = len(pending_tests_batch)

        if pending_test_count == 0:
            out("No pending tests found, exiting batch")
            return (
                ready_tests,
                test_builds_by_id,
                last_processed_test_id,
                skipped_no_build,
                pending_test_count,
            )

        last_processed_test_id = pending_tests_batch[-1].test_id

        pending_test_build_ids = {
            pending_test.build_id for pending_test in pending_tests_batch
        }
        found_test_builds = (
            Builds.objects.select_related("checkout")
            .only(
                "id",
                "status",
                "checkout__id",
                "checkout__start_time",
            )
            .in_bulk(pending_test_build_ids)
        )

        if not found_test_builds:
            out("No builds found for pending tests, skipping batch")
            return (
                ready_tests,
                test_builds_by_id,
                last_processed_test_id,
                skipped_no_build,
                pending_test_count,
            )

        for pending_test in pending_tests_batch:
            build = found_test_builds.get(pending_test.build_id)
            if not build:
                skipped_no_build += 1
                continue
            ready_tests.append(pending_test)
            test_builds_by_id[build.id] = build

        return (
            ready_tests,
            test_builds_by_id,
            last_processed_test_id,
            skipped_no_build,
            pending_test_count,
        )

    def _process_hardware_batch(
        self,
        ready_tests: Sequence[PendingTest],
        test_builds_by_id: dict[str, Builds],
    ) -> None:
        hardware_status_data, new_processed_entries_hardware = (
            aggregate_hardware_status(ready_tests, test_builds_by_id)
        )
        self._process_hardware_status(hardware_status_data)
        self._process_new_processed_entries(new_processed_entries_hardware)

    def _process_tree_listing_batch(
        self,
        ready_tests: Sequence[PendingTest],
        test_builds_by_id: dict[str, Builds],
        ready_builds: Sequence[PendingBuilds],
        build_checkouts_by_id: dict[str, Checkouts],
    ) -> None:
        tree_listing_data, new_processed_entries_tree = aggregate_tree_listing(
            ready_tests,
            test_builds_by_id,
            ready_builds,
            build_checkouts_by_id,
        )
        self._process_tree_listing(tree_listing_data)
        self._process_new_processed_entries(new_processed_entries_tree)

    def process_pending_batch(self, batch_size: int) -> int:
        last_processed_test_id = None
        last_processed_build_id = None
        tests_count = 0
        builds_count = 0

        while True:
            with transaction.atomic():
                out(
                    f"Starting batch processing "
                    f"(last_processed_test_id={str(last_processed_test_id)[:20]}, "
                    f"last_processed_build_id={str(last_processed_build_id)[:20]}, "
                    f"batch_size={batch_size})..."
                )
                t0 = time.time()

                (
                    ready_tests,
                    test_builds_by_id,
                    last_processed_test_id,
                    skipped_no_build,
                    pending_test_count,
                ) = self._get_ready_tests(
                    last_processed_test_id=last_processed_test_id,
                    batch_size=batch_size,
                )

                if ready_tests:
                    self._process_hardware_batch(ready_tests, test_builds_by_id)

                (
                    ready_builds,
                    build_checkouts_by_id,
                    last_processed_build_id,
                    skipped_no_checkout,
                    pending_build_count,
                ) = self._get_ready_builds(
                    last_processed_build_id=last_processed_build_id,
                    batch_size=batch_size,
                )

                if ready_tests or ready_builds:
                    self._process_tree_listing_batch(
                        ready_tests,
                        test_builds_by_id,
                        ready_builds,
                        build_checkouts_by_id,
                    )

                tests_count += self._delete_ready_tests(ready_tests=ready_tests)
                builds_count += self._delete_ready_builds(ready_builds=ready_builds)

                out(
                    f"Batch processed: {tests_count} tests aggregated, "
                    f"skipped (no build): {skipped_no_build}; "
                    f"{builds_count} builds aggregated, "
                    f"skipped (no checkout): {skipped_no_checkout}; "
                    f"in {time.time() - t0:.3f}s"
                )

                if pending_test_count == 0 and pending_build_count == 0:
                    out("No pending items found, exiting batch loop")
                    break

        return tests_count + builds_count
