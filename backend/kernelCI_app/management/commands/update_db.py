import ast
import csv
import json
import logging
import tarfile
from datetime import datetime, timedelta
from io import IOBase, StringIO, TextIOWrapper
from itertools import islice
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import Generator, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import connections, models
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from kernelCI_app.models import (
    Builds,
    Checkouts,
    HardwareStatus,
    Incidents,
    Issues,
    LatestCheckout,
    Tests,
    TreeListing,
    TreeTestsRollup,
)

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 1000
BUILD_BATCH_SIZE = 10000
TEST_BATCH_SIZE = 100000

SELECT_BATCH_SIZE = 25000

MAX_MEMORY_BUFFER_BYTES = 64 * 1024**2  # 64 MiB

csv.field_size_limit(1 * 1024**2)  # 1MiB row limit


def parse_array(array_str) -> Optional[list[str]]:
    try:
        array = ast.literal_eval(array_str)
        assert isinstance(array, list)
        return array
    except (ValueError, SyntaxError):
        return None


def parse_interval(interval_str: str) -> datetime:
    parts = interval_str.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid interval format: {interval_str}")

    value, unit = parts
    value = int(value)

    if unit.lower() in ["minute", "minutes"]:
        delta = timedelta(minutes=value)
    elif unit.lower() in ["hour", "hours"]:
        delta = timedelta(hours=value)
    elif unit.lower() in ["day", "days"]:
        delta = timedelta(days=value)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

    return timezone.now() - delta


def to_human_readable(num_bytes: int) -> str:
    """Converts bytes to a human-readable string (KiB, MiB, GiB)."""
    for unit in ["Bytes", "KiB", "MiB", "GiB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} TiB"


def ensure_suffix(filepath: str, suffix: str) -> Path:
    """Ensure path ends with .tar.gz without doubling when suffix already present."""
    p = Path(filepath)
    if p.name.lower().endswith(suffix):
        return p
    return p.with_suffix(suffix)


class Command(BaseCommand):
    help = "Migrate data dashboard_db to/from file"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_interval: str
        self.end_interval: str
        self.start_timestamp: datetime
        self.end_timestamp: datetime
        self.related_data_only: bool
        self.origins: list[str]
        self.origin_condition: str
        self.snapshot_archive: tarfile.TarFile

    def add_arguments(self, parser):

        command_parser = parser.add_subparsers(dest="command", required=True)
        snapshot_parser = command_parser.add_parser(
            "snapshot", help="Save snapshot of database into file."
        )

        snapshot_parser.add_argument(
            "--start-interval",
            type=str,
            help="Start interval for filtering data ('x days' or 'x hours' format)",
            required=True,
        )
        snapshot_parser.add_argument(
            "--end-interval",
            type=str,
            help="End interval for filtering data ('x days' or 'x hours' format)."
            " Optional, defaults to now ('0 hours').",
            required=False,
            default=None,
        )
        snapshot_parser.add_argument(
            "--table",
            type=str,
            help="""Table name to limit the migration to
              (optional, if not provided all tables will be migrated)""",
        )
        snapshot_parser.add_argument(
            "--related-data-only",
            action="store_true",
            help="""Only retrieves data that are related to the existing data.
                This allows to follow foreign key constraints,
                but it almost certainly won't retrieve all data in the given interval.""",
        )
        snapshot_parser.add_argument(
            "--origins",
            type=lambda s: [origin.strip() for origin in s.split(",")],
            help="Limit database changes to specific origins (comma-separated list)."
            " If not provided, any origin will be considered",
            default=[],
        )
        snapshot_parser.add_argument(
            "--filepath",
            type=str,
            required=True,
            help="Path to store/load the snapshot (.tar.gz) file.",
        )

        restore_parser = command_parser.add_parser(
            "restore",
            help="Load snapshot file onto database (will INSERT into database).",
        )
        restore_parser.add_argument(
            "--filepath",
            type=str,
            required=True,
            help="Path to store/load the snapshot (.tar.gz) file.",
        )

    def _invalid_table_error(self, table: str) -> str:
        return (
            f"Unknown table '{table}'.\n"
            "\tValid options are: issues, checkouts, builds, tests, incidents, "
            "latest_checkout, hardware_status, tree_listing, tree_tests_rollup."
        )

    def handle(self, *args, command, **options):
        if command == "snapshot":
            self.handle_snapshot(**options)
        elif command == "restore":
            self.handle_restore(**options)
        else:
            raise ValueError(f"Invalid command: {command}")

    def handle_restore(self, *args, filepath, **options):

        self.related_data_only = False
        filepath = ensure_suffix(filepath, ".tar.gz")
        self.restore(filepath)

    def handle_snapshot(
        self,
        *args,
        start_interval: str,
        end_interval: Optional[str],
        table: str,
        origins: list[str],
        related_data_only: bool,
        filepath: str,
        **options,
    ):
        end_interval_unsafe_tables = (
            None,
            "latest_checkout",
            "tree_listing",
            "tree_tests_rollup",
        )

        self.start_interval = start_interval
        self.end_interval = end_interval if end_interval is not None else "0 hours"
        self.related_data_only = related_data_only
        self.origins = origins
        self.origin_condition = (
            f"AND origin IN ({','.join(['%s'] * len(origins))})" if origins else ""
        )

        if end_interval is not None and table in end_interval_unsafe_tables:
            logger.warning(
                "--end-interval is set while snapshotting time aggregated tables"
                ", so an end interval may produce incorrect/stale data."
            )

        self.start_timestamp = parse_interval(self.start_interval)
        self.end_timestamp = parse_interval(self.end_interval)

        if self.end_timestamp <= self.start_timestamp:
            self.stdout.write(
                self.style.ERROR(
                    "End interval cannot be greater than start interval. Aborting."
                )
            )
            self.stdout.write(
                "Correct usage example: --start-interval='12 hours' --end-interval='0 hours'."
            )
            return

        self.stdout.write(
            f"\nFiltering data between {self.start_interval} and {self.end_interval}"
        )

        filepath = ensure_suffix(filepath, ".tar.gz")

        self.snapshot(table, filepath)

    def snapshot(self, table, snapshot_filepath: Path):

        self.snapshot_archive = tarfile.open(snapshot_filepath, "w:gz")

        try:
            match table:
                case None:
                    self.snapshot_issues()
                    self.snapshot_checkouts()
                    self.snapshot_builds()
                    self.snapshot_tests()
                    self.snapshot_incidents()
                    self.snapshot_latest_checkout()
                    self.snapshot_hardware_status()
                    self.snapshot_tree_listing()
                    self.snapshot_tree_tests_rollup()
                case "issues":
                    self.snapshot_issues()
                case "checkouts":
                    self.snapshot_checkouts()
                case "builds":
                    self.snapshot_builds()
                case "tests":
                    self.snapshot_tests()
                case "incidents":
                    self.snapshot_incidents()
                case "latest_checkout":
                    self.snapshot_latest_checkout()
                case "hardware_status":
                    self.snapshot_hardware_status()
                case "tree_listing":
                    self.snapshot_tree_listing()
                case "tree_tests_rollup":
                    self.snapshot_tree_tests_rollup()
                case _:
                    self.stdout.write(self._invalid_table_error(table))
            self.stdout.write(
                self.style.SUCCESS("Successfully migrated all data to dashboard_db")
            )
        except Exception as e:
            logger.error(f"Error updating database: {str(e)}")
            raise CommandError("Command failed") from e
        finally:
            self.snapshot_archive.close()

    def restore(self, snapshot_filepath: Path):
        self.snapshot_archive = tarfile.open(snapshot_filepath, "r:*")
        try:
            self.restore_checkouts()
            self.restore_builds()
            self.restore_issues()
            self.restore_tests()
            self.restore_incidents()
            self.restore_latest_checkout()
            self.restore_hardware_status()
            self.restore_tree_listing()
            self.restore_tree_tests_rollup()
            self.stdout.write(
                self.style.SUCCESS("Successfully migrated all data to dashboard_db")
            )
        except Exception as e:
            logger.error(f"Error updating database: {str(e)}")
            raise CommandError("Command failed") from e
        finally:
            self.snapshot_archive.close()

    def get_related_data(
        self, *, model: models.Model, field_name: str, filter_timestamp: bool = True
    ) -> tuple[set[str], str]:
        """Gets the related ids and makes the condition string"""

        # Avoids making an unnecessary query
        if self.related_data_only is False:
            return set(), ""

        values = model.objects
        if filter_timestamp:
            values = values.filter(
                field_timestamp__gte=self.start_timestamp,
                field_timestamp__lte=self.end_timestamp,
            )
        values = values.values_list("id", flat=True)
        related_ids = set(values)

        related_condition = (
            f"AND {field_name} IN ({','.join(['%s'] * len(related_ids))})"
        )

        return related_ids, related_condition

    # ISSUES ########################################
    def select_issues_data(self) -> list[tuple]:
        query = f"""
            SELECT _timestamp, id, version, origin, report_url, report_subject,
                   culprit_code, culprit_tool, culprit_harness, comment, misc,
                   categories
            FROM issues
                WHERE _timestamp >= NOW() - INTERVAL %s
                AND _timestamp <= NOW() - INTERVAL %s
                {self.origin_condition}
            ORDER BY _timestamp
        """
        query_params = [
            self.start_interval,
            self.end_interval,
        ] + self.origins

        with connections["default"].cursor() as kcidb_cursor:
            kcidb_cursor.execute(query, query_params)
            return kcidb_cursor.fetchall()

    def insert_issues_data(self, records: list[tuple]) -> int:
        total_inserted = 0

        original_issues = []
        for record in records:
            original_issues.append(
                Issues(
                    id=record[1],
                    version=record[2],
                    field_timestamp=parse_datetime(record[0]),
                    origin=record[3],
                    report_url=record[4],
                    report_subject=record[5],
                    culprit_code=record[6],
                    culprit_tool=record[7],
                    culprit_harness=record[8],
                    comment=record[9],
                    misc=json.loads(record[10]) if record[10] else None,
                    categories=parse_array(record[11]),
                )
            )

        migrated_issues = Issues.objects.bulk_create(
            original_issues,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )
        total_inserted = len(migrated_issues)

        self.stdout.write(f"Processed {total_inserted} Issues records")
        return total_inserted

    def snapshot_issues(self) -> None:
        """Migrate Issues data from dashboard_db to file"""
        with SpooledTemporaryFile(mode="w+b", max_size=MAX_MEMORY_BUFFER_BYTES) as file:
            self.stdout.write("\nMigrating Issues...")
            records = self.select_issues_data()
            self.insert_records(file, "issues", records)
            self.add_file_to_snapshot(file, "issues")
            self.stdout.write("Issues migration completed")

    def restore_issues(self) -> None:
        """Migrate Issues data from file to dashboard_db"""
        with TextIOWrapper(self.snapshot_archive.extractfile("issues.csv")) as file:
            self.stdout.write("\nMigrating Issues...")
            reader = csv.reader(file)
            records = self.read_records(reader)
            self.insert_issues_data(records)
            self.stdout.write("Issues migration completed")

    # CHECKOUTS ########################################
    def select_checkouts_data(self) -> list[tuple]:
        query = f"""
            SELECT _timestamp, id, origin, tree_name, git_repository_url,
                   git_commit_hash, git_commit_name, git_repository_branch,
                   patchset_files, patchset_hash, message_id, comment, start_time,
                   log_url, log_excerpt, valid, misc, git_commit_message,
                   git_repository_branch_tip, git_commit_tags,
                   origin_builds_finish_time, origin_tests_finish_time
            FROM checkouts
                WHERE _timestamp >= NOW() - INTERVAL %s
                AND _timestamp <= NOW() - INTERVAL %s
                {self.origin_condition}
            ORDER BY _timestamp
        """
        query_params = [
            self.start_interval,
            self.end_interval,
        ] + self.origins

        with connections["default"].cursor() as kcidb_cursor:
            kcidb_cursor.execute(query, query_params)
            return kcidb_cursor.fetchall()

    def insert_checkouts_data(self, records: list[tuple]) -> int:
        original_checkouts = []

        for record in records:
            original_checkouts.append(
                Checkouts(
                    field_timestamp=parse_datetime(record[0]),
                    id=record[1],
                    origin=record[2],
                    tree_name=record[3],
                    git_repository_url=record[4],
                    git_commit_hash=record[5],
                    git_commit_name=record[6],
                    git_repository_branch=record[7],
                    patchset_files=json.loads(record[8]) if record[8] else None,
                    patchset_hash=record[9],
                    message_id=record[10],
                    comment=record[11],
                    start_time=parse_datetime(record[12]),
                    log_url=record[13],
                    log_excerpt=record[14],
                    valid=record[15],
                    misc=json.loads(record[16]) if record[16] else None,
                    git_commit_message=record[17],
                    git_repository_branch_tip=record[18],
                    git_commit_tags=parse_array(record[19]),
                    origin_builds_finish_time=record[20] or None,
                    origin_tests_finish_time=record[21] or None,
                )
            )

        migrated_checkouts = Checkouts.objects.bulk_create(
            original_checkouts,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )

        total_inserted = len(migrated_checkouts)

        self.stdout.write(f"Processed {total_inserted} Checkouts records")
        return total_inserted

    def snapshot_checkouts(self) -> None:
        """Migrate Checkouts data from dashboard_db to file"""

        with SpooledTemporaryFile(mode="w+b", max_size=MAX_MEMORY_BUFFER_BYTES) as file:
            self.stdout.write("\nMigrating Checkouts...")
            records = self.select_checkouts_data()
            self.insert_records(file, "checkouts", records)
            self.add_file_to_snapshot(file, "checkouts")
            self.stdout.write("Checkouts migration completed")

    def restore_checkouts(self) -> None:
        """Migrate Checkouts data from file to dashboard_db"""

        with TextIOWrapper(self.snapshot_archive.extractfile("checkouts.csv")) as file:
            reader = csv.reader(file)
            self.stdout.write("\nMigrating Checkouts...")
            records = self.read_records(reader)
            self.insert_checkouts_data(records)
            self.stdout.write("Checkouts migration completed")

    # BUILDS ########################################
    def select_builds_data(self) -> list[tuple]:
        related_checkout_ids, related_condition = self.get_related_data(
            model=Checkouts, field_name="checkout_id"
        )
        if self.related_data_only and len(related_checkout_ids) == 0:
            return []

        query = f"""
            SELECT _timestamp, checkout_id, id, origin, comment, start_time,
                   duration, architecture, command, compiler, input_files,
                   output_files, config_name, config_url, log_url, log_excerpt,
                   misc, status
            FROM builds
            WHERE _timestamp >= NOW() - INTERVAL %s
            AND _timestamp <= NOW() - INTERVAL %s
            {related_condition}
            {self.origin_condition}
            ORDER BY _timestamp, id
        """
        query_params = (
            [
                self.start_interval,
                self.end_interval,
            ]
            + list(related_checkout_ids)
            + self.origins
        )

        with connections["default"].cursor() as kcidb_cursor:
            kcidb_cursor.execute(query, query_params)
            return kcidb_cursor.fetchall()

    def write_to_csv_stream(self, records: list[tuple]) -> StringIO:
        stream = StringIO()
        writer = csv.writer(stream)
        writer.writerows(records)
        return stream

    def read_records(
        self, reader: csv.reader, max_rows: Optional[int] = None
    ) -> list[tuple]:
        records = [tuple(record) for record in islice(reader, max_rows)]
        return records

    def insert_records(self, tmp_file: IOBase, table: str, records: list[tuple]):
        stream = self.write_to_csv_stream(records)
        csv_bytes = stream.getvalue().encode("utf-8")
        tmp_file.write(csv_bytes)
        self.stdout.write(
            f"\nProcessed {len(records)} {table} records: {to_human_readable(len(csv_bytes))}"
        )

    def snapshot_builds(self) -> None:
        """Migrate Builds data from dashboard_db to file,
        only inserts builds that have the related checkout in the dashboard_db
        in order to preserve the foreign key constraint"""
        with SpooledTemporaryFile(mode="w+b", max_size=MAX_MEMORY_BUFFER_BYTES) as file:
            self.stdout.write("\nMigrating Builds...")
            records = self.select_builds_data()
            self.insert_records(file, "builds", records)
            self.add_file_to_snapshot(file, "builds")
            self.stdout.write("Builds migration completed")

    def restore_builds(self) -> None:
        """Migrate Builds data from file to dashboard_db,
        only inserts builds that have the related checkout in the dashboard_db
        in order to preserve the foreign key constraint"""
        with TextIOWrapper(self.snapshot_archive.extractfile("builds.csv")) as file:
            self.stdout.write("\nMigrating Builds...")
            reader = csv.reader(file)
            records = self.read_records(reader)
            self.insert_builds_data(records)
            self.stdout.write("Builds migration completed")

    def insert_builds_data(self, records: list[tuple]) -> int:
        original_builds: list[Builds] = [
            Builds(
                field_timestamp=parse_datetime(record[0]),
                checkout_id=record[1],
                id=record[2],
                origin=record[3],
                comment=record[4],
                start_time=parse_datetime(record[5]),
                duration=record[6] or None,
                architecture=record[7],
                command=record[8],
                compiler=record[9],
                input_files=json.loads(record[10]) if record[10] else None,
                output_files=json.loads(record[11]) if record[11] else None,
                config_name=record[12],
                config_url=record[13],
                log_url=record[14],
                log_excerpt=record[15],
                misc=json.loads(record[16]) if record[16] else None,
                status=record[17],
            )
            for record in records
        ]

        migrated_builds = Builds.objects.bulk_create(
            original_builds,
            ignore_conflicts=True,
            batch_size=BUILD_BATCH_SIZE,
        )
        total_inserted = len(migrated_builds)

        self.stdout.write(f"Processed {total_inserted} Builds records")
        return total_inserted

    # TESTS ########################################
    def select_tests_data(self) -> Generator[list[tuple], None, list[tuple]]:
        related_build_ids, related_condition = self.get_related_data(
            model=Builds, field_name="build_id"
        )
        if self.related_data_only and len(related_build_ids) == 0:
            return []

        tests_query = f"""
            SELECT _timestamp, build_id, id, origin, environment_comment,
                    environment_misc, path, comment, log_url, log_excerpt,
                    status, start_time, duration, output_files, misc,
                    number_value, environment_compatible, number_prefix,
                    number_unit, input_files
            FROM tests
            WHERE _timestamp >= NOW() - INTERVAL %s
            AND _timestamp <= NOW() - INTERVAL %s
            {related_condition}
            {self.origin_condition}
            ORDER BY _timestamp, id
        """
        query_params = (
            [
                self.start_interval,
                self.end_interval,
            ]
            + list(related_build_ids)
            + self.origins
        )

        with connections["default"].cursor() as kcidb_cursor:
            kcidb_cursor.execute(tests_query, query_params)
            self.stdout.write("Finished fetching tests")
            while batch := kcidb_cursor.fetchmany(SELECT_BATCH_SIZE):
                yield batch

    def insert_tests_data(self, records: list[tuple]) -> int:
        print(f"Processing {len(records)} tests")
        original_tests: list[Tests] = [
            Tests(
                field_timestamp=parse_datetime(record[0]),
                build_id=record[1],
                id=record[2],
                origin=record[3],
                environment_comment=record[4],
                environment_misc=json.loads(record[5]) if record[5] else None,
                path=record[6],
                comment=record[7],
                log_url=record[8],
                log_excerpt=record[9],
                status=record[10],
                start_time=parse_datetime(record[11]) if record[11] else None,
                duration=record[12] or None,
                output_files=json.loads(record[13]) if record[13] else None,
                misc=json.loads(record[14]) if record[14] else None,
                number_value=record[15] or None,
                environment_compatible=parse_array(record[16]),
                number_prefix=record[17],
                number_unit=record[18],
                input_files=json.loads(record[19]) if record[19] else None,
            )
            for record in records
        ]

        migrated_tests = Tests.objects.bulk_create(
            original_tests,
            ignore_conflicts=True,
            batch_size=TEST_BATCH_SIZE,
        )
        total_inserted = len(migrated_tests)

        self.stdout.write(f"Processed {total_inserted} Tests records")
        return total_inserted

    def add_file_to_snapshot(self, file: IOBase, table: str):
        tar_info = tarfile.TarInfo(name=f"{table}.csv")
        file.seek(0, 2)
        tar_info.size = file.tell()
        file.seek(0, 0)
        self.snapshot_archive.addfile(tar_info, file)

    def snapshot_tests(self) -> None:
        """Migrate Tests data from dashboard_db to file,
        only inserts tests that have the related build in the dashboard_db
        in order to preserve the foreign key constraint"""
        with SpooledTemporaryFile(mode="w+b", max_size=MAX_MEMORY_BUFFER_BYTES) as file:
            self.stdout.write("\nMigrating Tests...")
            records = self.select_tests_data()
            for record_batch in records:
                self.insert_records(file, "tests", record_batch)
            self.add_file_to_snapshot(file, "tests")
            self.stdout.write("Tests migration completed")

    def restore_tests(self) -> None:
        """Migrate Tests data from file to dashboard_db,
        only inserts tests that have the related build in the dashboard_db
        in order to preserve the foreign key constraint"""
        with TextIOWrapper(self.snapshot_archive.extractfile("tests.csv")) as file:
            self.stdout.write("\nMigrating Tests...")
            reader = csv.reader(file)
            while records := self.read_records(reader, max_rows=TEST_BATCH_SIZE):
                self.insert_tests_data(records)
            self.stdout.write("Tests migration completed")

    # INCIDENTS ########################################
    def select_incidents_data(self) -> list[tuple]:
        related_issue_ids, related_condition = self.get_related_data(
            model=Issues, field_name="issue_id", filter_timestamp=False
        )
        if self.related_data_only and len(related_issue_ids) == 0:
            return []

        # Though we can filter with the build and test ID, filtering by
        # issue ID is more consistent since incidents can be triggered for
        # an old build/test and filtering with all build/test ids is also costly
        query = f"""
            SELECT _timestamp, id, origin, issue_id, issue_version,
                   build_id, test_id, present, comment, misc
            FROM incidents
            WHERE _timestamp >= NOW() - INTERVAL %s
            AND _timestamp <= NOW() - INTERVAL %s
            {related_condition}
            {self.origin_condition}
            ORDER BY _timestamp
        """

        query_params = (
            [
                self.start_interval,
                self.end_interval,
            ]
            + list(related_issue_ids)
            + self.origins
        )

        with connections["default"].cursor() as kcidb_cursor:
            kcidb_cursor.execute(query, query_params)
            records = kcidb_cursor.fetchall()
            print(f"Retrieved {len(records)} Incidents")
            return records

    def insert_incidents_data(self, records: list[tuple]) -> int:
        original_incidents: list[Incidents] = []
        existing_issue_ids: set[tuple[str, int]] = set()
        existing_build_ids: set[str] = set()
        existing_test_ids: set[str] = set()
        skipped_incidents = 0

        if self.related_data_only:
            proposed_issue_ids: set[tuple[str, int]] = set()
            proposed_build_ids: set[str] = set()
            proposed_test_ids: set[str] = set()

            for record in records:
                issue_id = record[3]
                issue_version = record[4]
                build_id = record[5]
                test_id = record[6]
                proposed_issue_ids.add((issue_id, issue_version))
                if build_id:
                    proposed_build_ids.add(build_id)
                if test_id:
                    proposed_test_ids.add(test_id)

            existing_issue_ids = set(
                Issues.objects.filter(
                    id__in=[issue[0] for issue in proposed_issue_ids]
                ).values_list("id", flat=True)
            )

            existing_build_ids = set(
                Builds.objects.filter(id__in=proposed_build_ids).values_list(
                    "id", flat=True
                )
            )

            existing_test_ids = set(
                Tests.objects.filter(id__in=proposed_test_ids).values_list(
                    "id", flat=True
                )
            )

        # Incidents that don't have a related issue, build or test in the dashboard_db
        # will be skipped to preserve the foreign key constraints unless explicited
        for record in records:
            issue_id = record[3]
            issue_version = record[4]
            build_id = record[5]
            test_id = record[6]

            if not self.related_data_only or issue_id in existing_issue_ids:
                if (
                    (build_id is not None and build_id not in existing_build_ids)
                    or (test_id is not None and test_id not in existing_test_ids)
                ) and self.related_data_only:
                    skipped_incidents += 1
                    continue

                original_incidents.append(
                    Incidents(
                        field_timestamp=record[0],
                        id=record[1],
                        origin=record[2],
                        issue_id=issue_id,
                        issue_version=issue_version,
                        build_id=build_id,
                        test_id=test_id,
                        present=record[7],
                        comment=record[8],
                        misc=json.loads(record[9]) if record[9] else None,
                    )
                )
            else:
                skipped_incidents += 1

        migrated_incidents = Incidents.objects.bulk_create(
            original_incidents,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )
        total_inserted = len(migrated_incidents)

        self.stdout.write(
            f"Processed {total_inserted} Incidents records (skipped {skipped_incidents})"
        )
        return total_inserted

    def snapshot_incidents(self) -> None:
        """Migrate Incidents data from dashboard_db to file,
        incidents are related to issues, builds and tests.
        So if any of them are not null, an incident will only be inserted
        if the related issue, build or test exists in the dashboard_db"""

        with SpooledTemporaryFile(mode="w+b", max_size=MAX_MEMORY_BUFFER_BYTES) as file:
            self.stdout.write("\nMigrating Incidents...")
            records = self.select_incidents_data()
            self.insert_records(file, "incidents", records)
            self.add_file_to_snapshot(file, "incidents")
            self.stdout.write("Incidents migration completed")

    def restore_incidents(self) -> None:
        """Migrate Incidents data from file to dashboard_db,
        incidents are related to issues, builds and tests.
        So if any of them are not null, an incident will only be inserted
        if the related issue, build or test exists in the dashboard_db"""

        with TextIOWrapper(self.snapshot_archive.extractfile("incidents.csv")) as file:
            self.stdout.write("\nMigrating Incidents...")
            reader = csv.reader(file)
            records = self.read_records(reader)
            self.insert_incidents_data(records)
            self.stdout.write("Incidents migration completed")

    # LATEST CHECKOUT ########################################
    def select_latest_checkout_data(self) -> list[tuple]:
        query = f"""
            SELECT checkout_id, origin, tree_name, git_repository_url,
                   git_repository_branch, start_time
            FROM latest_checkout
            WHERE start_time >= NOW() - INTERVAL %s
            AND start_time <= NOW() - INTERVAL %s
            {self.origin_condition}
            ORDER BY start_time, checkout_id
        """
        query_params = [
            self.start_interval,
            self.end_interval,
        ] + self.origins

        with connections["default"].cursor() as kcidb_cursor:
            kcidb_cursor.execute(query, query_params)
            return kcidb_cursor.fetchall()

    def insert_latest_checkout_data(self, records: list[tuple]) -> int:
        original_latest_checkout: list[LatestCheckout] = [
            LatestCheckout(
                checkout_id=record[0],
                origin=record[1],
                tree_name=record[2],
                git_repository_url=record[3],
                git_repository_branch=record[4],
                start_time=parse_datetime(record[5]) if record[5] else None,
            )
            for record in records
        ]

        migrated_latest_checkout = LatestCheckout.objects.bulk_create(
            original_latest_checkout,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )
        total_inserted = len(migrated_latest_checkout)

        self.stdout.write(f"Processed {total_inserted} LatestCheckout records")
        return total_inserted

    def snapshot_latest_checkout(self) -> None:
        """Migrate LatestCheckout data from default to dashboard_db"""
        with SpooledTemporaryFile(mode="w+b", max_size=MAX_MEMORY_BUFFER_BYTES) as file:
            self.stdout.write("\nMigrating LatestCheckout...")
            records = self.select_latest_checkout_data()
            self.insert_records(file, "latest_checkout", records)
            self.add_file_to_snapshot(file, "latest_checkout")
            self.stdout.write("LatestCheckout migration completed")

    def restore_latest_checkout(self) -> None:
        """Migrate LatestCheckout data from default to dashboard_db"""
        with TextIOWrapper(
            self.snapshot_archive.extractfile("latest_checkout.csv")
        ) as file:
            self.stdout.write("\nMigrating LatestCheckout...")
            reader = csv.reader(file)
            records = self.read_records(reader)
            self.insert_latest_checkout_data(records)
            self.stdout.write("LatestCheckout migration completed")

    # HARDWARE STATUS ########################################
    def select_hardware_status_data(self) -> list[tuple]:
        origin_condition = (
            f"AND test_origin IN ({','.join(['%s'] * len(self.origins))})"
            if self.origins
            else ""
        )
        query = f"""
            SELECT checkout_id, test_origin, platform, compatibles, start_time,
                   build_pass, build_failed, build_inc,
                   boot_pass, boot_failed, boot_inc,
                   test_pass, test_failed, test_inc
            FROM hardware_status
            WHERE start_time >= NOW() - INTERVAL %s
            AND start_time <= NOW() - INTERVAL %s
            {origin_condition}
            ORDER BY start_time, test_origin, platform, checkout_id
        """
        query_params = [
            self.start_interval,
            self.end_interval,
        ] + self.origins

        with connections["default"].cursor() as kcidb_cursor:
            kcidb_cursor.execute(query, query_params)
            return kcidb_cursor.fetchall()

    def insert_hardware_status_data(self, records: list[tuple]) -> int:
        original_hardware_status: list[HardwareStatus] = [
            HardwareStatus(
                checkout_id=record[0],
                test_origin=record[1],
                platform=record[2],
                compatibles=parse_array(record[3]),
                start_time=parse_datetime(record[4]) if record[4] else None,
                build_pass=record[5] or 0,
                build_failed=record[6] or 0,
                build_inc=record[7] or 0,
                boot_pass=record[8] or 0,
                boot_failed=record[9] or 0,
                boot_inc=record[10] or 0,
                test_pass=record[11] or 0,
                test_failed=record[12] or 0,
                test_inc=record[13] or 0,
            )
            for record in records
        ]

        migrated_hardware_status = HardwareStatus.objects.bulk_create(
            original_hardware_status,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )
        total_inserted = len(migrated_hardware_status)

        self.stdout.write(f"Processed {total_inserted} HardwareStatus records")
        return total_inserted

    def snapshot_hardware_status(self) -> None:
        """Migrate HardwareStatus data from dashboard_db to file"""
        with SpooledTemporaryFile(mode="w+b", max_size=MAX_MEMORY_BUFFER_BYTES) as file:
            self.stdout.write("\nMigrating HardwareStatus...")
            records = self.select_hardware_status_data()
            self.insert_records(file, "hardware_status", records)
            self.add_file_to_snapshot(file, "hardware_status")
            self.stdout.write("HardwareStatus migration completed")

    def restore_hardware_status(self) -> None:
        """Migrate HardwareStatus data from file to dashboard_db"""
        with TextIOWrapper(
            self.snapshot_archive.extractfile("hardware_status.csv")
        ) as file:
            self.stdout.write("\nMigrating HardwareStatus...")
            reader = csv.reader(file)
            records = self.read_records(reader)
            self.insert_hardware_status_data(records)
            self.stdout.write("HardwareStatus migration completed")

    # TREE LISTING ########################################
    def select_tree_listing_data(self) -> list[tuple]:
        query = f"""
            SELECT checkout_id, origin, tree_name, git_repository_url,
                   git_repository_branch, git_commit_hash, git_commit_name,
                   git_commit_tags, start_time, build_pass, build_failed, build_inc,
                   boot_pass, boot_failed, boot_inc, test_pass, test_failed, test_inc
            FROM tree_listing
            WHERE start_time >= NOW() - INTERVAL %s
            AND start_time <= NOW() - INTERVAL %s
            {self.origin_condition}
            ORDER BY start_time, checkout_id
        """
        query_params = [
            self.start_interval,
            self.end_interval,
        ] + self.origins

        with connections["default"].cursor() as kcidb_cursor:
            kcidb_cursor.execute(query, query_params)
            return kcidb_cursor.fetchall()

    def insert_tree_listing_data(self, records: list[tuple]) -> int:
        original_tree_listing: list[TreeListing] = [
            TreeListing(
                checkout_id=record[0],
                origin=record[1],
                tree_name=record[2],
                git_repository_url=record[3],
                git_repository_branch=record[4],
                git_commit_hash=record[5],
                git_commit_name=record[6],
                git_commit_tags=parse_array(record[7]),
                start_time=parse_datetime(record[8]) if record[8] else None,
                build_pass=record[9] or 0,
                build_failed=record[10] or 0,
                build_inc=record[11] or 0,
                boot_pass=record[12] or 0,
                boot_failed=record[13] or 0,
                boot_inc=record[14] or 0,
                test_pass=record[15] or 0,
                test_failed=record[16] or 0,
                test_inc=record[17] or 0,
            )
            for record in records
        ]

        migrated_tree_listing = TreeListing.objects.bulk_create(
            original_tree_listing,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )
        total_inserted = len(migrated_tree_listing)

        self.stdout.write(f"Processed {total_inserted} TreeListing records")
        return total_inserted

    def snapshot_tree_listing(self) -> None:
        """Migrate TreeListing data from dashboard_db to file"""
        with SpooledTemporaryFile(mode="w+b", max_size=MAX_MEMORY_BUFFER_BYTES) as file:
            self.stdout.write("\nMigrating TreeListing...")
            records = self.select_tree_listing_data()
            self.insert_records(file, "tree_listing", records)
            self.add_file_to_snapshot(file, "tree_listing")
            self.stdout.write("TreeListing migration completed")

    def restore_tree_listing(self) -> None:
        """Migrate TreeListing data from file to dashboard_db"""
        with TextIOWrapper(
            self.snapshot_archive.extractfile("tree_listing.csv")
        ) as file:
            self.stdout.write("\nMigrating TreeListing...")
            reader = csv.reader(file)
            records = self.read_records(reader)
            self.insert_tree_listing_data(records)
            self.stdout.write("TreeListing migration completed")

    # TREE TESTS ROLLUP ########################################
    def select_tree_tests_rollup_data(
        self,
    ) -> Generator[list[tuple], None, list[tuple]]:
        origin_condition = (
            f"AND tree_tests_rollup.origin IN ({','.join(['%s'] * len(self.origins))})"
            if self.origins
            else ""
        )
        query = f"""
            SELECT origin, tree_name, git_repository_branch, git_repository_url,
                   git_commit_hash, path_group, build_config_name,
                   build_architecture, build_compiler, hardware_key, test_platform,
                   test_lab, test_origin, issue_id, issue_version,
                   issue_uncategorized, is_boot, pass_tests, fail_tests, skip_tests,
                   error_tests, miss_tests, done_tests, null_tests, total_tests
            FROM tree_tests_rollup
            WHERE EXISTS (
                SELECT 1
                FROM checkouts
                WHERE checkouts.start_time >= NOW() - INTERVAL %s
                AND checkouts.start_time <= NOW() - INTERVAL %s
                AND checkouts.origin = tree_tests_rollup.origin
                AND checkouts.tree_name IS NOT DISTINCT FROM tree_tests_rollup.tree_name
                AND checkouts.git_repository_branch IS NOT DISTINCT FROM
                    tree_tests_rollup.git_repository_branch
                AND checkouts.git_repository_url IS NOT DISTINCT FROM
                    tree_tests_rollup.git_repository_url
                AND checkouts.git_commit_hash IS NOT DISTINCT FROM
                    tree_tests_rollup.git_commit_hash
            )
            {origin_condition}
            ORDER BY origin, tree_name, git_repository_branch, git_repository_url,
                     git_commit_hash, path_group
        """
        query_params = [
            self.start_interval,
            self.end_interval,
        ] + self.origins

        with connections["default"].cursor() as kcidb_cursor:
            kcidb_cursor.execute(query, query_params)
            self.stdout.write("Finished fetching tree_tests_rollup")
            while batch := kcidb_cursor.fetchmany(SELECT_BATCH_SIZE):
                yield batch

    def insert_tree_tests_rollup_data(self, records: list[tuple]) -> int:
        original_tree_tests_rollup: list[TreeTestsRollup] = [
            TreeTestsRollup(
                origin=record[0],
                tree_name=record[1],
                git_repository_branch=record[2],
                git_repository_url=record[3],
                git_commit_hash=record[4],
                path_group=record[5],
                build_config_name=record[6],
                build_architecture=record[7],
                build_compiler=record[8],
                hardware_key=record[9],
                test_platform=record[10],
                test_lab=record[11],
                test_origin=record[12],
                issue_id=record[13],
                issue_version=record[14] or None,
                issue_uncategorized=record[15],
                is_boot=record[16],
                pass_tests=record[17] or 0,
                fail_tests=record[18] or 0,
                skip_tests=record[19] or 0,
                error_tests=record[20] or 0,
                miss_tests=record[21] or 0,
                done_tests=record[22] or 0,
                null_tests=record[23] or 0,
                total_tests=record[24] or 0,
            )
            for record in records
        ]

        migrated_tree_tests_rollup = TreeTestsRollup.objects.bulk_create(
            original_tree_tests_rollup,
            ignore_conflicts=True,
            batch_size=TEST_BATCH_SIZE,
        )
        total_inserted = len(migrated_tree_tests_rollup)

        self.stdout.write(f"Processed {total_inserted} TreeTestsRollup records")
        return total_inserted

    def snapshot_tree_tests_rollup(self) -> None:
        """Migrate TreeTestsRollup data from dashboard_db to file"""
        with SpooledTemporaryFile(mode="w+b", max_size=MAX_MEMORY_BUFFER_BYTES) as file:
            self.stdout.write("\nMigrating TreeTestsRollup...")
            records = self.select_tree_tests_rollup_data()
            for record_batch in records:
                self.insert_records(file, "tree_tests_rollup", record_batch)
            self.add_file_to_snapshot(file, "tree_tests_rollup")
            self.stdout.write("TreeTestsRollup migration completed")

    def restore_tree_tests_rollup(self) -> None:
        """Migrate TreeTestsRollup data from file to dashboard_db"""
        with TextIOWrapper(
            self.snapshot_archive.extractfile("tree_tests_rollup.csv")
        ) as file:
            self.stdout.write("\nMigrating TreeTestsRollup...")
            reader = csv.reader(file)
            while records := self.read_records(reader, max_rows=TEST_BATCH_SIZE):
                self.insert_tree_tests_rollup_data(records)
            self.stdout.write("TreeTestsRollup migration completed")
