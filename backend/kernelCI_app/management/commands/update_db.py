import json
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
import logging
from kernelCI_app.models import Issues, Checkouts, Builds, Tests, Incidents
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 1000
BUILD_BATCH_SIZE = 10000
TEST_BATCH_SIZE = 100000

SELECT_BATCH_SIZE = 25000


def parse_interval(interval_str: str):
    now = timezone.now()
    parts = interval_str.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid interval format: {interval_str}")

    value, unit = parts
    value = int(value)

    if unit.lower() in ["hour", "hours"]:
        delta = timedelta(hours=value)
    elif unit.lower() in ["day", "days"]:
        delta = timedelta(days=value)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

    return now - delta


class Command(BaseCommand):
    help = "Migrate data from default database to dashboard_db"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_interval = None
        self.end_interval = None
        self.start_timestamp = None
        self.end_timestamp = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-interval",
            type=str,
            help="Start interval for filtering data ('x days' or 'x hours' format)",
        )
        parser.add_argument(
            "--end-interval",
            type=str,
            help="End interval for filtering data ('x days' or 'x hours' format)",
        )
        parser.add_argument(
            "--table",
            type=str,
            help="""Table name to limit the migration to
              (optional, if not provided all tables will be migrated)""",
        )

    def handle(self, *args, **options):
        self.start_interval = options.get("start_interval")
        self.end_interval = options.get("end_interval")
        table = options.get("table", None)

        if not self.start_interval or not self.end_interval:
            self.stdout.write(
                self.style.ERROR(
                    "Both self.start_interval and self.end_interval must be provided. Aborting."
                )
            )
            return

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

        try:
            match table:
                case None:
                    self.migrate_issues()
                    self.migrate_checkouts()
                    self.migrate_builds()
                    self.migrate_tests()
                    self.migrate_incidents()
                case "issues":
                    self.migrate_issues()
                case "checkouts":
                    self.migrate_checkouts()
                case "builds":
                    self.migrate_builds()
                case "tests":
                    self.migrate_tests()
                case "incidents":
                    self.migrate_incidents()
                case _:
                    self.stdout.write(
                        self.style.ERROR(
                            f"""Unknown table '{table}'.
                                Valid options are: issues, checkouts, builds, tests, incidents."""
                        )
                    )

            self.stdout.write(
                self.style.SUCCESS("Successfully migrated all data to dashboard_db")
            )
        except Exception as e:
            logger.error(f"Error updating database: {str(e)}")
            raise CommandError("Command failed") from e

    # ISSUES ########################################
    def select_issues_data(self) -> tuple:
        query = """
            SELECT _timestamp, id, version, origin, report_url, report_subject,
                   culprit_code, culprit_tool, culprit_harness, comment, misc,
                   categories
            FROM issues
                WHERE _timestamp >= NOW() - INTERVAL %(start_interval)s
                AND _timestamp <= NOW() - INTERVAL %(end_interval)s
            ORDER BY _timestamp
        """
        params = {
            "start_interval": self.start_interval,
            "end_interval": self.end_interval,
        }

        with connections["default"].cursor() as default_cursor:
            default_cursor.execute(query, params)
            return default_cursor.fetchall()

    def insert_issues_data(self, records: tuple) -> int:
        total_inserted = 0

        original_issues = []
        for record in records:
            original_issues.append(
                Issues(
                    id=record[1],
                    version=record[2],
                    field_timestamp=record[0],
                    origin=record[3],
                    report_url=record[4],
                    report_subject=record[5],
                    culprit_code=record[6],
                    culprit_tool=record[7],
                    culprit_harness=record[8],
                    comment=record[9],
                    misc=json.loads(record[10]) if record[10] else None,
                    categories=record[11],
                )
            )

        migrated_issues = Issues.objects.using("dashboard_db").bulk_create(
            original_issues,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )
        total_inserted = len(migrated_issues)

        self.stdout.write(f"Processed {total_inserted} Issues records")
        return total_inserted

    def migrate_issues(self):
        """Migrate Issues data from default to dashboard_db"""

        self.stdout.write("\nMigrating Issues...")
        records = self.select_issues_data()
        self.insert_issues_data(records)
        self.stdout.write("Issues migration completed")

    # CHECKOUTS ########################################
    def select_checkouts_data(self) -> tuple:
        query = """
            SELECT _timestamp, id, origin, tree_name, git_repository_url,
                   git_commit_hash, git_commit_name, git_repository_branch,
                   patchset_files, patchset_hash, message_id, comment, start_time,
                   log_url, log_excerpt, valid, misc, git_commit_message,
                   git_repository_branch_tip, git_commit_tags,
                   origin_builds_finish_time, origin_tests_finish_time
            FROM checkouts
                WHERE _timestamp >= NOW() - INTERVAL %(start_interval)s
                AND _timestamp <= NOW() - INTERVAL %(end_interval)s
            ORDER BY _timestamp
        """
        params = {
            "start_interval": self.start_interval,
            "end_interval": self.end_interval,
        }

        with connections["default"].cursor() as default_cursor:
            default_cursor.execute(query, params)
            return default_cursor.fetchall()

    def insert_checkouts_data(self, records: tuple) -> int:
        original_checkouts = []

        for record in records:
            original_checkouts.append(
                Checkouts(
                    field_timestamp=record[0],
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
                    start_time=record[12],
                    log_url=record[13],
                    log_excerpt=record[14],
                    valid=record[15],
                    misc=json.loads(record[16]) if record[16] else None,
                    git_commit_message=record[17],
                    git_repository_branch_tip=record[18],
                    git_commit_tags=record[19],
                    origin_builds_finish_time=record[20],
                    origin_tests_finish_time=record[21],
                )
            )

        migrated_checkouts = Checkouts.objects.using("dashboard_db").bulk_create(
            original_checkouts,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )

        total_inserted = len(migrated_checkouts)

        self.stdout.write(f"Processed {total_inserted} Checkouts records")
        return total_inserted

    def migrate_checkouts(self) -> None:
        """Migrate Checkouts data from default to dashboard_db"""

        self.stdout.write("\nMigrating Checkouts...")
        records = self.select_checkouts_data()
        self.insert_checkouts_data(records)
        self.stdout.write("Checkouts migration completed")
        return

    # BUILDS ########################################
    def select_builds_data(self) -> tuple:
        checkout_ids = set(
            (
                Checkouts.objects.using("dashboard_db")
                .filter(
                    field_timestamp__gte=self.start_timestamp,
                    field_timestamp__lte=self.end_timestamp,
                )
                .values_list("id", flat=True)
            )
        )
        checkout_id_placeholders = ",".join(["%s"] * len(checkout_ids))

        query = f"""
            SELECT _timestamp, checkout_id, id, origin, comment, start_time,
                   duration, architecture, command, compiler, input_files,
                   output_files, config_name, config_url, log_url, log_excerpt,
                   misc, status
            FROM builds
            WHERE builds.checkout_id IN ({checkout_id_placeholders})
            AND _timestamp >= NOW() - INTERVAL %s
            AND _timestamp <= NOW() - INTERVAL %s
            ORDER BY _timestamp, id
        """

        with connections["default"].cursor() as default_cursor:
            default_cursor.execute(
                query, list(checkout_ids) + [self.start_interval, self.end_interval]
            )
            return default_cursor.fetchall()

    def insert_builds_data(self, records: tuple) -> int:
        original_builds: list[Builds] = [
            Builds(
                field_timestamp=record[0],
                checkout_id=record[1],
                id=record[2],
                origin=record[3],
                comment=record[4],
                start_time=record[5],
                duration=record[6],
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

        migrated_builds = Builds.objects.using("dashboard_db").bulk_create(
            original_builds,
            ignore_conflicts=True,
            batch_size=BUILD_BATCH_SIZE,
        )
        total_inserted = len(migrated_builds)

        self.stdout.write(f"Processed {total_inserted} Builds records")
        return total_inserted

    def migrate_builds(self) -> None:
        """Migrate Builds data from default to dashboard_db,
        only inserts builds that have the related checkout in the dashboard_db
        in order to preserve the foreign key constraint"""
        self.stdout.write("\nMigrating Builds...")

        records = self.select_builds_data()
        self.insert_builds_data(records)
        self.stdout.write("Builds migration completed")

    # TESTS ########################################
    def select_tests_data(self):
        existing_build_ids = set(
            Builds.objects.using("dashboard_db")
            .filter(
                field_timestamp__gte=self.start_timestamp,
                field_timestamp__lte=self.end_timestamp,
            )
            .values_list("id", flat=True)
        )
        build_id_placeholders = ",".join(["%s"] * len(existing_build_ids))

        tests_query = f"""
            SELECT _timestamp, build_id, id, origin, environment_comment,
                    environment_misc, path, comment, log_url, log_excerpt,
                    status, start_time, duration, output_files, misc,
                    number_value, environment_compatible, number_prefix,
                    number_unit, input_files
            FROM tests
            WHERE build_id IN ({build_id_placeholders})
            AND _timestamp >= NOW() - INTERVAL %s
            AND _timestamp <= NOW() - INTERVAL %s
            ORDER BY _timestamp, id
        """
        query_params = list(existing_build_ids) + [
            self.start_interval,
            self.end_interval,
        ]

        with connections["default"].cursor() as default_cursor:
            default_cursor.execute(tests_query, query_params)
            self.stdout.write("Finished fetching tests")
            while batch := default_cursor.fetchmany(SELECT_BATCH_SIZE):
                yield batch

    def insert_tests_data(self, records) -> int:
        print(f"Processing {len(records)} tests")
        original_tests: list[Tests] = [
            Tests(
                field_timestamp=record[0],
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
                start_time=record[11],
                duration=record[12],
                output_files=json.loads(record[13]) if record[13] else None,
                misc=json.loads(record[14]) if record[14] else None,
                number_value=record[15],
                environment_compatible=record[16],
                number_prefix=record[17],
                number_unit=record[18],
                input_files=json.loads(record[19]) if record[19] else None,
            )
            for record in records
        ]

        migrated_tests = Tests.objects.using("dashboard_db").bulk_create(
            original_tests,
            ignore_conflicts=True,
            batch_size=TEST_BATCH_SIZE,
        )
        total_inserted = len(migrated_tests)

        self.stdout.write(f"Processed {total_inserted} Tests records")
        return total_inserted

    def migrate_tests(self) -> None:
        """Migrate Tests data from default to dashboard_db,
        only inserts tests that have the related build in the dashboard_db
        in order to preserve the foreign key constraint"""

        self.stdout.write("\nMigrating Tests...")
        total_inserted = 0
        for batch in self.select_tests_data():
            inserted = self.insert_tests_data(batch)
            total_inserted += inserted
        self.stdout.write(
            f"\nTests migration completed.\nInserted {total_inserted} tests in total."
        )

    # INCIDENTS ########################################
    def select_incidents_data(self) -> tuple:
        existing_issues_ids = set(
            Issues.objects.using("dashboard_db").values_list("id", flat=True)
        )
        issue_id_placeholders = ",".join(["%s"] * len(existing_issues_ids))

        # Though we can filter with the build and test ID, filtering by
        # issue ID is more consistent since incidents can be triggered for
        # an old build/test and filtering with all build/test ids is also costly
        query = f"""
            SELECT _timestamp, id, origin, issue_id, issue_version,
                   build_id, test_id, present, comment, misc
            FROM incidents
            WHERE issue_id IN ({issue_id_placeholders})
            AND _timestamp >= NOW() - INTERVAL %s
            AND _timestamp <= NOW() - INTERVAL %s
            ORDER BY _timestamp
        """

        query_params = list(existing_issues_ids) + [
            self.start_interval,
            self.end_interval,
        ]

        with connections["default"].cursor() as default_cursor:
            default_cursor.execute(query, query_params)
            records = default_cursor.fetchall()
            print(f"Retrieved {len(records)} Incidents")
            return records

    def insert_incidents_data(self, records: tuple) -> int:
        original_incidents: list[Incidents] = []
        proposed_issue_ids: set[tuple[str, int]] = set()
        proposed_build_ids: set[str] = set()
        proposed_test_ids: set[str] = set()
        skipped_incidents = 0

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
            Issues.objects.using("dashboard_db")
            .filter(id__in=[issue[0] for issue in proposed_issue_ids])
            .values_list("id", flat=True)
        )

        existing_build_ids = set(
            Builds.objects.using("dashboard_db")
            .filter(id__in=proposed_build_ids)
            .values_list("id", flat=True)
        )

        existing_test_ids = set(
            Tests.objects.using("dashboard_db")
            .filter(id__in=proposed_test_ids)
            .values_list("id", flat=True)
        )

        # Incidents that don't have a related issue, build or test in the dashboard_db
        # will be skipped to preserve the foreign key constraints
        for record in records:
            issue_id = record[3]
            issue_version = record[4]
            build_id = record[5]
            test_id = record[6]

            if issue_id in existing_issue_ids:
                if (build_id is not None and build_id not in existing_build_ids) or (
                    test_id is not None and test_id not in existing_test_ids
                ):
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

        migrated_incidents = Incidents.objects.using("dashboard_db").bulk_create(
            original_incidents,
            ignore_conflicts=True,
            batch_size=DEFAULT_BATCH_SIZE,
        )
        total_inserted = len(migrated_incidents)

        self.stdout.write(
            f"Processed {total_inserted} Incidents records (skipped {skipped_incidents})"
        )
        return total_inserted

    def migrate_incidents(self) -> None:
        """Migrate Incidents data from default to dashboard_db,
        incidents are related to issues, builds and tests.
        So if any of them are not null, an incident will only be inserted
        if the related issue, build or test exists in the dashboard_db"""

        self.stdout.write("\nMigrating Incidents...")
        records = self.select_incidents_data()
        self.insert_incidents_data(records)
        self.stdout.write("Incidents migration completed")
