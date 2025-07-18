import json
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
import logging
from kernelCI_app.models import Issues, Checkouts, Builds, Tests, Incidents

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 1000
BUILD_BATCH_SIZE = 10000
TEST_BATCH_SIZE = 100000


class Command(BaseCommand):
    help = "Migrate data from default database to dashboard_db"

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
        start_interval = options.get("start_interval")
        end_interval = options.get("end_interval")
        table = options.get("table", None)

        if not start_interval or not end_interval:
            self.stdout.write(
                self.style.ERROR(
                    "Both start_interval and end_interval must be provided. Aborting."
                )
            )
            return

        self.stdout.write(
            f"\nFiltering data between {start_interval} and {end_interval}"
        )

        try:
            if table is None:
                self.migrate_issues(start_interval, end_interval)
                self.migrate_checkouts(start_interval, end_interval)
                self.migrate_builds(start_interval, end_interval)
                self.migrate_tests(start_interval, end_interval)
                self.migrate_incidents(start_interval, end_interval)
            else:
                match table:
                    case "issues":
                        self.migrate_issues(start_interval, end_interval)
                    case "checkouts":
                        self.migrate_checkouts(start_interval, end_interval)
                    case "builds":
                        self.migrate_builds(start_interval, end_interval)
                    case "tests":
                        self.migrate_tests(start_interval, end_interval)
                    case "incidents":
                        self.migrate_incidents(start_interval, end_interval)
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
            raise CommandError(f"Command failed: {str(e)}")

    # ISSUES ########################################
    def select_issues_data(self, start_interval: str, end_interval: str) -> tuple:
        """Select data from the default database using raw SQL with interval filtering"""
        default_cursor = connections["default"].cursor()
        query = """
            SELECT _timestamp, id, version, origin, report_url, report_subject,
                   culprit_code, culprit_tool, culprit_harness, comment, misc,
                   categories
            FROM issues
                WHERE _timestamp >= NOW() - INTERVAL %(start_interval)s
                AND _timestamp <= NOW() - INTERVAL %(end_interval)s
            ORDER BY _timestamp
        """
        params = {"start_interval": start_interval, "end_interval": end_interval}

        default_cursor.execute(query, params)
        return default_cursor.fetchall()

    def insert_issues_data(self, records: tuple) -> int:
        """Insert data into dashboard_db using Django models"""
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

    def migrate_issues(self, start_interval, end_interval):
        """Migrate Issues data from default to dashboard_db"""
        self.stdout.write("\nMigrating Issues...")
        records = self.select_issues_data(start_interval, end_interval)
        self.insert_issues_data(records)
        self.stdout.write("Issues migration completed")

    # CHECKOUTS ########################################
    def select_checkouts_data(self, start_interval: str, end_interval: str) -> tuple:
        """Select data from the default database using raw SQL with interval filtering"""
        default_cursor = connections["default"].cursor()
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
        params = {"start_interval": start_interval, "end_interval": end_interval}

        default_cursor.execute(query, params)
        return default_cursor.fetchall()

    def insert_checkouts_data(self, records: tuple) -> int:
        """Insert data into dashboard_db using Django models"""
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

    def migrate_checkouts(self, start_interval, end_interval) -> None:
        """Migrate Checkouts data from default to dashboard_db

        Returns the list of ids of the checkouts that were inserted"""
        self.stdout.write("\nMigrating Checkouts...")
        records = self.select_checkouts_data(start_interval, end_interval)
        self.insert_checkouts_data(records)
        self.stdout.write("Checkouts migration completed")
        return

    # BUILDS ########################################
    def select_builds_data(self, start_interval: str, end_interval: str) -> tuple:
        """Select data from the default database using raw SQL with interval filtering"""
        default_cursor = connections["default"].cursor()
        query = """
            SELECT _timestamp, checkout_id, id, origin, comment, start_time,
                   duration, architecture, command, compiler, input_files,
                   output_files, config_name, config_url, log_url, log_excerpt,
                   misc, status
            FROM builds
            WHERE _timestamp >= NOW() - INTERVAL %(start_interval)s
            AND _timestamp <= NOW() - INTERVAL %(end_interval)s
            ORDER BY _timestamp, id
        """
        params = {"start_interval": start_interval, "end_interval": end_interval}

        default_cursor.execute(query, params)
        return default_cursor.fetchall()

    def insert_builds_data(self, records: tuple) -> int:
        """Insert data into dashboard_db using Django models"""
        original_builds: list[Builds] = []
        skipped_builds = 0
        proposed_checkout_ids: list[str] = [record[1] for record in records]

        existing_checkouts = Checkouts.objects.using("dashboard_db").filter(
            id__in=proposed_checkout_ids
        )
        existing_checkouts_map: dict[str, Checkouts] = {
            checkout.id: checkout for checkout in existing_checkouts
        }
        existing_checkout_ids = existing_checkouts_map.keys()

        # Builds that don't have a related checkout in the dashboard_db
        # will be skipped to preserve the foreign key constraint
        for record in records:
            checkout_id = record[1]
            if checkout_id in existing_checkout_ids:
                original_builds.append(
                    Builds(
                        field_timestamp=record[0],
                        checkout=existing_checkouts_map[checkout_id],
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
                )
            else:
                skipped_builds += 1

        migrated_builds = Builds.objects.using("dashboard_db").bulk_create(
            original_builds,
            ignore_conflicts=True,
            batch_size=BUILD_BATCH_SIZE,
        )
        total_inserted = len(migrated_builds)

        self.stdout.write(
            f"Processed {total_inserted} Builds records (skipped {skipped_builds})"
        )
        return total_inserted

    def migrate_builds(self, start_interval: str, end_interval: str) -> None:
        """Migrate Builds data from default to dashboard_db,
        only inserts builds that have the related checkout in the dashboard_db
        in order to preserve the foreign key constraint"""
        self.stdout.write("\nMigrating Builds...")
        records = self.select_builds_data(start_interval, end_interval)
        self.insert_builds_data(records)
        self.stdout.write("Builds migration completed")

    # TESTS ########################################
    def select_tests_data(self, start_interval: str, end_interval: str) -> tuple:
        """Select data from the default database using raw SQL with interval filtering"""
        default_cursor = connections["default"].cursor()
        query = """
            SELECT _timestamp, build_id, id, origin, environment_comment,
                   environment_misc, path, comment, log_url, log_excerpt,
                   status, start_time, duration, output_files, misc,
                   number_value, environment_compatible, number_prefix,
                   number_unit, input_files
            FROM tests
            WHERE _timestamp >= NOW() - INTERVAL %(start_interval)s
            AND _timestamp <= NOW() - INTERVAL %(end_interval)s
            ORDER BY _timestamp, id
        """
        params = {"start_interval": start_interval, "end_interval": end_interval}

        default_cursor.execute(query, params)
        return default_cursor.fetchall()

    def insert_tests_data(self, records: tuple) -> int:
        """Insert data into dashboard_db using Django models"""
        original_tests: list[Tests] = []
        skipped_tests = 0
        proposed_build_ids: list[str] = [record[1] for record in records]

        existing_builds = Builds.objects.using("dashboard_db").filter(
            id__in=proposed_build_ids
        )
        existing_builds_map: dict[str, Builds] = {
            build.id: build for build in existing_builds
        }
        existing_build_ids = existing_builds_map.keys()

        # Tests that don't have a related build in the dashboard_db
        # will be skipped to preserve the foreign key constraint
        for record in records:
            build_id = record[1]
            if build_id in existing_build_ids:
                original_tests.append(
                    Tests(
                        field_timestamp=record[0],
                        build=existing_builds_map[build_id],
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
                )
            else:
                skipped_tests += 1

        migrated_tests = Tests.objects.using("dashboard_db").bulk_create(
            original_tests,
            ignore_conflicts=True,
            batch_size=TEST_BATCH_SIZE,
        )
        total_inserted = len(migrated_tests)

        self.stdout.write(
            f"Processed {total_inserted} Tests records (skipped {skipped_tests})"
        )
        return total_inserted

    def migrate_tests(self, start_interval: str, end_interval: str) -> None:
        """Migrate Tests data from default to dashboard_db"""
        self.stdout.write("\nMigrating Tests...")
        records = self.select_tests_data(start_interval, end_interval)
        self.insert_tests_data(records)
        self.stdout.write("Tests migration completed")

    # INCIDENTS ########################################
    def select_incidents_data(self, start_interval: str, end_interval: str) -> tuple:
        """Select data from the default database using raw SQL with interval filtering"""
        default_cursor = connections["default"].cursor()
        query = """
            SELECT _timestamp, id, origin, issue_id, issue_version,
                   build_id, test_id, present, comment, misc
            FROM incidents
            WHERE _timestamp >= NOW() - INTERVAL %(start_interval)s
            AND _timestamp <= NOW() - INTERVAL %(end_interval)s
            ORDER BY _timestamp, id
        """
        params = {"start_interval": start_interval, "end_interval": end_interval}

        default_cursor.execute(query, params)
        return default_cursor.fetchall()

    def insert_incidents_data(self, records: tuple) -> int:
        """Insert data into dashboard_db using Django models"""
        original_incidents: list[Incidents] = []
        proposed_issue_ids: list[tuple[str, int]] = []
        proposed_build_ids: list[str] = []
        proposed_test_ids: list[str] = []
        skipped_incidents = 0

        for record in records:
            issue_id = record[3]
            issue_version = record[4]
            build_id = record[5]
            test_id = record[6]
            proposed_issue_ids.append((issue_id, issue_version))
            if build_id:
                proposed_build_ids.append(build_id)
            if test_id:
                proposed_test_ids.append(test_id)

        existing_issues = Issues.objects.using("dashboard_db").filter(
            id__in=[issue[0] for issue in proposed_issue_ids]
        )
        existing_issues_map: dict[tuple[str, int], Issues] = {
            (issue.id, issue.version): issue for issue in existing_issues
        }
        existing_issue_keys = existing_issues_map.keys()

        existing_builds_map: dict[str, Builds] = {}
        if proposed_build_ids:
            existing_builds = Builds.objects.using("dashboard_db").filter(
                id__in=proposed_build_ids
            )
            existing_builds_map = {build.id: build for build in existing_builds}

        existing_tests_map: dict[str, Tests] = {}
        if proposed_test_ids:
            existing_tests = Tests.objects.using("dashboard_db").filter(
                id__in=proposed_test_ids
            )
            existing_tests_map = {test.id: test for test in existing_tests}

        # Incidents that don't have a related issue, build or test in the dashboard_db
        # will be skipped to preserve the foreign key constraints
        for record in records:
            issue_id = record[3]
            issue_version = record[4]
            build_id = record[5]
            test_id = record[6]
            issue_key = (issue_id, issue_version)

            if issue_key in existing_issue_keys:
                build_obj = existing_builds_map.get(build_id) if build_id else None
                test_obj = existing_tests_map.get(test_id) if test_id else None

                if build_id and build_obj is None:
                    skipped_incidents += 1
                    continue

                if test_id and test_obj is None:
                    skipped_incidents += 1
                    continue

                original_incidents.append(
                    Incidents(
                        field_timestamp=record[0],
                        id=record[1],
                        origin=record[2],
                        issue=existing_issues_map[issue_key],
                        issue_version=issue_version,
                        build=build_obj,
                        test=test_obj,
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

    def migrate_incidents(self, start_interval: str, end_interval: str) -> None:
        """Migrate Incidents data from default to dashboard_db"""
        self.stdout.write("\nMigrating Incidents...")
        records = self.select_incidents_data(start_interval, end_interval)
        self.insert_incidents_data(records)
        self.stdout.write("Incidents migration completed")
