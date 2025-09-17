"""
Management command to seed test database with realistic data.
"""

import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from kernelCI_app.tests.factories import (
    CheckoutFactory,
    BuildFactory,
    TestFactory,
    IssueFactory,
    IncidentFactory,
)
from kernelCI_app.models import (
    Issues,
    Tests,
    Builds,
    Checkouts,
    Incidents,
)
from kernelCI_app.tests.factories.mocks import Build, Issue, Test
from kernelCI_app.helpers.system import get_running_instance


class Command(BaseCommand):
    help = "Seed test database with realistic data for integration tests"

    def add_arguments(self, parser):
        parser.add_argument(
            "--checkouts",
            type=int,
            default=50,
            help="Number of checkouts to create (default: 50)",
        )
        parser.add_argument(
            "--issues",
            type=int,
            default=20,
            help="Number of issues to create (default: 20)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding. This will delete ALL data from the database.",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip confirmation prompts for clear operations.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._validate_clear_operation(skip_confirmation=options["yes"])
            self.stdout.write("Clearing existing data...")
            self.clear_data()

        self.stdout.write("Seeding test database with realistic data...")

        with transaction.atomic():
            checkouts = self.create_checkouts(count=options["checkouts"])
            builds = self.create_builds(checkouts=checkouts)
            tests = self.create_tests_and_boots(builds=builds)
            issues = self.create_issues(count=options["issues"])
            incidents = self.create_incidents(issues=issues, builds=builds, tests=tests)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded database with:\n"
                f"- {len(checkouts)} checkouts\n"
                f"- {len(builds)} builds\n"
                f"- {len(tests)} tests\n"
                f"- {len(issues)} issues\n"
                f"- {len(incidents)} incidents\n"
            )
        )

    def _validate_clear_operation(self, *, skip_confirmation: bool) -> None:
        """Validate that clear operation is safe to proceed."""
        running_instance = get_running_instance()

        if running_instance == "production" or running_instance == "staging":
            self.stdout.write(
                self.style.ERROR(
                    f"{running_instance.upper()} ENVIRONMENT DETECTED!\n"
                    f"Data clearing is DISABLED in {running_instance} environments."
                )
            )
            sys.exit(1)

        if not skip_confirmation:
            confirmation = input("Type 'yes' to confirm data deletion:")
            if confirmation.lower() != "yes":
                self.stdout.write("Input is not 'yes'. Operation cancelled.")
                sys.exit(1)

        self.stdout.write(
            f"Clearing all data from {running_instance or 'local'} environment..."
        )

    def clear_data(self) -> None:
        """Clear existing test data."""
        Incidents.objects.all().delete()
        Issues.objects.all().delete()
        Tests.objects.all().delete()
        Builds.objects.all().delete()
        Checkouts.objects.all().delete()

    def create_checkouts(self, *, count: int) -> list[Checkouts]:
        """Create checkouts with realistic data including specific test data."""
        self.stdout.write(f"Creating {count} checkouts...")

        checkouts = []

        for _ in range(count):
            checkout = CheckoutFactory.create()
            checkouts.append(checkout)

        return checkouts

    def create_builds(self, *, checkouts: list[Checkouts]) -> list[Builds]:
        """Create builds for checkouts."""
        self.stdout.write("Creating builds...")

        builds = []
        for checkout in checkouts:
            build_ids = Build.get_builds_for_checkout(checkout.id)

            for specific_build_id in build_ids:
                build_data = Build.get_build_data(specific_build_id)
                if build_data:
                    build = BuildFactory.create(
                        checkout=checkout,
                        origin=build_data.get("origin", checkout.origin),
                        architecture=build_data.get("architecture", None),
                        config_name=build_data.get("config_name", "defconfig"),
                        status=build_data.get("status", None),
                        id=specific_build_id,
                    )
                    builds.append(build)

        return builds

    def create_tests_and_boots(self, *, builds: list[Builds]) -> list[Tests]:
        """Create tests and boots for builds."""
        self.stdout.write("Creating tests...")
        tests = []

        # Create tests with specific IDs
        failed_build = next((b for b in builds if b.id == "failed_tests_build"), None)
        if failed_build:
            for test_id in Test.get_all_test_ids():
                test = TestFactory.create(
                    id=test_id,
                    origin=failed_build.origin,
                    build=failed_build,
                )
                tests.append(test)

        for build in builds:
            if build.id == "amlogic_build_valid":
                test = TestFactory.create(
                    build=build,
                    origin=build.origin,
                    path="boot.boot_test",
                )
                tests.append(test)
                test = TestFactory.create(
                    build=build,
                    origin=build.origin,
                    path="test.test_test",
                )
                tests.append(test)
            else:
                test = TestFactory.create(
                    build=build,
                    origin=build.origin,
                )
                tests.append(test)

        return tests

    def create_issues(self, *, count: int) -> list[Issues]:
        """Create issues including specific test data."""
        self.stdout.write(f"Creating {count} issues...")

        issues = []

        for _ in range(count):
            issue = IssueFactory.create()
            issues.append(issue)

        return issues

    def create_incidents(
        self, *, issues: list[Issues], builds: list[Builds], tests: list[Tests]
    ) -> list[Incidents]:
        """Create incidents - only essential ones for tests."""
        incidents = []
        self.stdout.write("Creating only essential incidents for tests...")
        for issue in issues:
            issue_data = Issue.get_issue_data(issue.id)
            if issue_data:
                # Create build incidents
                for build_id in Issue.get_issue_build_ids(issue.id):
                    build = next((b for b in builds if b.id == build_id), None)
                    if build:
                        incident = IncidentFactory.create(
                            issue=issue,
                            build=build,
                            origin=issue.origin,
                            issue_version=issue.version,
                        )
                        incidents.append(incident)
                # Create test incidents
                for test_id in Issue.get_issue_test_ids(issue.id):
                    test = next((t for t in tests if t.id == test_id), None)
                    if test:
                        incident = IncidentFactory.create(
                            issue=issue,
                            test=test,
                            origin=issue.origin,
                            issue_version=issue.version,
                        )
                        incidents.append(incident)

        return incidents
