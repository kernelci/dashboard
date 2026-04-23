from django.core.management.base import BaseCommand

from kernelCI_app.tests.unitTests.commands.fixtures.metrics_notifications_data import (
    METRICS_NOTIFICATIONS_EXAMPLE_FILEPATH,
)
from kernelCI_app.tests.unitTests.commands.metrics_notifications_test import (
    TestMetricsReportTemplate,
)


class Command(BaseCommand):
    help = (
        "Refreshes the txt file used as an example and comparison "
        "for the metrics notification unit tests. "
        "Run this manually when the template changes."
    )

    def handle(self, *args, **options):
        try:
            content = TestMetricsReportTemplate.render_report()
            with open(METRICS_NOTIFICATIONS_EXAMPLE_FILEPATH, "w") as f:
                f.write(content)
            self.stdout.write(
                self.style.SUCCESS(f"{METRICS_NOTIFICATIONS_EXAMPLE_FILEPATH} updated.")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to update metrics_report_example.txt: {e}")
            )
