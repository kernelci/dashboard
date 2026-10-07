from django.core.management.base import BaseCommand, CommandError

from kernelCI_app.management.commands.helpers.healthcheck import (
    MONITORING_ID_PARAM_HELP_TEXT,
    run_with_healthcheck_monitoring,
)
from kernelCI_app.middleware.backendRequestMetricsMiddleware import (
    publish_visitor_requests,
    resolve_publish_analytics_date,
)


class Command(BaseCommand):
    help = (
        "Publish per-visitor request-count bands for a UTC analytics day "
        "(default: yesterday). Writes Prometheus counters; requires "
        "PROMETHEUS_MULTIPROC_DIR when run outside the metrics worker."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            default=None,
            help=(
                "Finished UTC analytics date (YYYY-MM-DD). "
                "Default: yesterday. Today is refused."
            ),
        )
        parser.add_argument(
            "--monitoring-id",
            type=str,
            default="publish_visitor_requests",
            help=MONITORING_ID_PARAM_HELP_TEXT,
        )

    def handle(self, *args, **options):
        try:
            analytics_date = resolve_publish_analytics_date(options["date"])
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        def action():
            publish_visitor_requests(analytics_date)
            return analytics_date

        published_date = run_with_healthcheck_monitoring(
            monitoring_id=options["monitoring_id"],
            action=action,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Published visitor request counts for {published_date}."
            )
        )
