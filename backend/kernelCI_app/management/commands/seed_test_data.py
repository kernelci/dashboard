"""
Management command to seed test database with realistic data.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from kernelCI_app.tests.factories import (
    CheckoutFactory,
    BuildFactory,
    TestFactory,
    IssueFactory,
    IncidentFactory,
)
from kernelCI_app.tests.factories.mocks import Build, Issue


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
            "--clear", action="store_true", help="Clear existing data before seeding"
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            self.clear_data()

        self.stdout.write("Seeding test database with realistic data...")

        with transaction.atomic():
            checkouts = self.create_checkouts(options["checkouts"])

            builds = self.create_builds(checkouts)

            tests = self.create_tests_and_boots(builds)

            issues = self.create_issues(options["issues"])

            self.create_incidents(issues, builds, tests)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded database with:\n"
                f"- {len(checkouts)} checkouts\n"
                f"- {len(builds)} builds\n"
                f"- {len(tests)} tests\n"
                f"- {len(issues)} issues\n"
            )
        )

    def clear_data(self):
        """Clear existing test data."""
        from kernelCI_app.models import (
            Issues,
            Tests,
            Builds,
            Checkouts,
            Incidents,
        )

        Incidents.objects.all().delete()
        Issues.objects.all().delete()
        Tests.objects.all().delete()
        Builds.objects.all().delete()
        Checkouts.objects.all().delete()

    def create_checkouts(self, count):
        """Create checkouts with realistic data including specific test data."""
        self.stdout.write(f"Creating {count} checkouts...")

        checkouts = []

        for _ in range(count):
            checkout = CheckoutFactory.create()
            checkouts.append(checkout)

        return checkouts

    def create_builds(self, checkouts):
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

    def create_tests_and_boots(self, builds):
        """Create tests and boots for builds."""
        self.stdout.write("Creating tests...")
        tests = []
        test_ids = [
            "maestro:67b898cdf7707533c0067a02",
            "maestro:67bd70e6323b35c54a8824a0",
            "test_issue_test",
        ]
        checkout = CheckoutFactory.create()
        build = BuildFactory.create(
            id="failed_tests_build",
            origin="maestro",
            config_name="defconfig",
            architecture="x86_64",
            status="FAIL",
            checkout=checkout,
        )

        for test_id in test_ids:
            test = TestFactory.create(
                id=test_id,
                origin=build.origin,
                build=build,
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

    def create_issues(self, count):
        """Create issues including specific test data."""
        self.stdout.write(f"Creating {count} issues...")

        issues = []

        for _ in range(count):
            issue = IssueFactory.create()
            issues.append(issue)

        return issues

    def create_incidents(self, issues, builds, tests):
        """Create incidents - only essential ones for tests."""
        self.stdout.write("Creating only essential incidents for tests...")
        for issue in issues:
            issue_data = Issue.get_issue_data(issue.id)
            if issue_data:
                # Create build incidents
                for build_id in Issue.get_issue_build_ids(issue.id):
                    build = next((b for b in builds if b.id == build_id), None)
                    if build:
                        IncidentFactory.create(
                            issue=issue,
                            build=build,
                            origin=issue.origin,
                            issue_version=issue.version,
                        )
                        self.stdout.write(
                            f"Created build incident for: {build.id} with issue: {issue.id}"
                        )

                # Create test incidents
                for test_id in Issue.get_issue_test_ids(issue.id):
                    test = next((t for t in tests if t.id == test_id), None)
                    if test:
                        IncidentFactory.create(
                            issue=issue,
                            test=test,
                            origin=issue.origin,
                            issue_version=issue.version,
                        )
                        self.stdout.write(
                            f"Created test incident for: {test.id} with issue: {issue.id}"
                        )
