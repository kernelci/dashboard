from django.core.management.base import BaseCommand

from kernelCI_app.tests.unitTests.commands.fixtures.report_notifications_data import (
    ISSUE_BOOT_REPORT_EXAMPLE_FILEPATH,
    ISSUE_BUILD_REPORT_EXAMPLE_FILEPATH,
    TEST_REPORT_EXAMPLE_FILEPATH,
)
from kernelCI_app.tests.unitTests.commands.report_notifications_test import (
    TestReportTemplates,
)


class Command(BaseCommand):
    help = (
        "Refreshes the example report fixtures used by the report notification "
        "unit tests. Run this manually when a report template changes."
    )

    def handle(self, *args, **options):
        outputs = [
            (
                ISSUE_BUILD_REPORT_EXAMPLE_FILEPATH,
                TestReportTemplates.render_build_report(),
            ),
            (
                ISSUE_BOOT_REPORT_EXAMPLE_FILEPATH,
                TestReportTemplates.render_boot_report(),
            ),
            (TEST_REPORT_EXAMPLE_FILEPATH, TestReportTemplates.render_test_report()),
        ]
        for filepath, content in outputs:
            with open(filepath, "w") as f:
                f.write(content)
            self.stdout.write(self.style.SUCCESS(f"{filepath} updated."))
