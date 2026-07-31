"""Recompute the hardware daily aggregates from checkouts, builds and tests.

A day is rewritten wholesale, so the command keeps no dedupe state, is idempotent and
lets the grain change without a data migration. Tests arrive long after their checkout,
so days stay mutable for months and are rebuilt on a window kept inside raw retention.
If a rebuild finds no raw rows for a day that had aggregates, the transaction rolls
back and keeps the existing rows.
"""

from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX
from kernelCI_app.helpers.database import table_lock_id
from kernelCI_app.helpers.logger import out
from kernelCI_app.management.commands.helpers.healthcheck import (
    MONITORING_ID_PARAM_HELP_TEXT,
    run_with_healthcheck_monitoring,
)

# A null path is a plain test, and any status but PASS/FAIL is inconclusive. The day is a
# half open UTC range, so the start_time index is usable and the bucket does not follow
# the session time zone.
DAY_TESTS = """
    SELECT
        c.id AS checkout_id,
        t.origin,
        COALESCE(NULLIF(t.misc ->> 'runtime', ''), t.origin) AS lab,
        t.environment_misc ->> 'platform' AS platform,
        t.environment_compatible AS compatibles,
        COALESCE(t.path = 'boot' OR t.path LIKE 'boot.%%', false) AS is_boot,
        t.status,
        b.id AS build_id,
        b.origin AS build_origin,
        COALESCE(
            NULLIF(b.misc ->> 'lab', ''), NULLIF(b.misc ->> 'runtime', ''), b.origin
        ) AS build_lab,
        b.status AS build_status
    FROM tests t
    JOIN builds b ON b.id = t.build_id
    JOIN checkouts c ON c.id = b.checkout_id
    WHERE c.start_time >= %(day)s::timestamp AT TIME ZONE 'UTC'
      AND c.start_time < (%(day)s::date + 1)::timestamp AT TIME ZONE 'UTC'
      AND t.environment_misc ->> 'platform' IS NOT NULL
"""

# One label per platform, the longest compatible chain reported for it: the shortest
# ones name the SoC family instead of the board. Labs disagree, and a label per lab
# would list one board twice.
PLATFORM_COMPATIBLES = """
    SELECT DISTINCT ON (checkout_id, platform) checkout_id, platform, compatibles
    FROM day_tests
    WHERE compatibles IS NOT NULL
    ORDER BY checkout_id, platform, cardinality(compatibles) DESC, compatibles
"""

MATERIALIZE_DAY_TESTS = f"""
CREATE TEMP TABLE day_tests ON COMMIT DROP AS
{DAY_TESTS}
"""

MATERIALIZE_PLATFORM_COMPATIBLES = f"""
CREATE TEMP TABLE platform_compatibles ON COMMIT DROP AS
{PLATFORM_COMPATIBLES}
"""

INSERT_TESTS = """
INSERT INTO hardware_daily_tests (
    checkout_day, checkout_id, test_origin, test_lab, platform, compatibles,
    boot_pass, boot_failed, boot_inc, test_pass, test_failed, test_inc
)
WITH counted AS (
    SELECT
        checkout_id,
        origin,
        lab,
        platform,
        count(*) FILTER (WHERE is_boot AND status = 'PASS') AS boot_pass,
        count(*) FILTER (WHERE is_boot AND status = 'FAIL') AS boot_failed,
        count(*) FILTER (WHERE is_boot
            AND status IS DISTINCT FROM 'PASS'
            AND status IS DISTINCT FROM 'FAIL') AS boot_inc,
        count(*) FILTER (WHERE NOT is_boot AND status = 'PASS') AS test_pass,
        count(*) FILTER (WHERE NOT is_boot AND status = 'FAIL') AS test_failed,
        count(*) FILTER (WHERE NOT is_boot
            AND status IS DISTINCT FROM 'PASS'
            AND status IS DISTINCT FROM 'FAIL') AS test_inc
    FROM day_tests
    GROUP BY checkout_id, origin, lab, platform
)
SELECT
    %(day)s,
    c.checkout_id,
    c.origin,
    c.lab,
    c.platform,
    pc.compatibles,
    c.boot_pass, c.boot_failed, c.boot_inc, c.test_pass, c.test_failed, c.test_inc
FROM counted c
LEFT JOIN platform_compatibles pc USING (checkout_id, platform)
"""

# A build has no platform of its own, so it lands on every platform its tests ran on,
# but never keyed by test dimensions, which would count it once per test lab. DISTINCT
# collapses the fan-out, otherwise a build is counted once per test.
INSERT_BUILDS = f"""
INSERT INTO hardware_daily_builds (
    checkout_day, checkout_id, build_origin, build_lab, platform, compatibles,
    build_pass, build_failed, build_inc
)
WITH day_builds AS (
    SELECT DISTINCT checkout_id, build_id, build_origin, build_lab, platform,
                    build_status
    FROM day_tests
    WHERE build_id NOT LIKE '{MAESTRO_DUMMY_BUILD_PREFIX}%%'
),
counted AS (
    SELECT
        checkout_id,
        build_origin,
        build_lab,
        platform,
        count(*) FILTER (WHERE build_status = 'PASS') AS build_pass,
        count(*) FILTER (WHERE build_status = 'FAIL') AS build_failed,
        count(*) FILTER (WHERE build_status IS DISTINCT FROM 'PASS'
            AND build_status IS DISTINCT FROM 'FAIL') AS build_inc
    FROM day_builds
    GROUP BY checkout_id, build_origin, build_lab, platform
)
SELECT
    %(day)s,
    c.checkout_id,
    c.build_origin,
    c.build_lab,
    c.platform,
    pc.compatibles,
    c.build_pass, c.build_failed, c.build_inc
FROM counted c
LEFT JOIN platform_compatibles pc USING (checkout_id, platform)
"""


class Command(BaseCommand):
    help = "Recompute the hardware daily aggregates from checkouts, builds and tests"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=1,
            help="Days to recompute back from today, kept below the prune_db retention",
        )
        parser.add_argument(
            "--day",
            type=date.fromisoformat,
            help="Recompute a single day (YYYY-MM-DD) instead of the recent window",
        )
        parser.add_argument(
            "--monitoring-id",
            type=str,
            default=None,
            help=MONITORING_ID_PARAM_HELP_TEXT,
        )

    def handle(self, *args, **options):
        return run_with_healthcheck_monitoring(
            monitoring_id=options.get("monitoring_id"),
            action=lambda: self._run_action(options),
        )

    def _run_action(self, options):
        today = timezone.now().date()
        days = (
            [options["day"]]
            if options["day"]
            else [
                today - timedelta(days=offset)
                for offset in reversed(range(options["days"]))
            ]
        )

        for day in days:
            self._recompute_day(day)

    def _recompute_day(self, day: date) -> None:
        deleted = inserted = 0
        tables = ("hardware_daily_builds", "hardware_daily_tests")
        inserts = (INSERT_BUILDS, INSERT_TESTS)

        with transaction.atomic(), connection.cursor() as cursor:
            for table in tables:
                # Overlapping runs rebuilding one day collide on the primary key, and
                # the winner reads the same raw rows, so the loser can skip.
                cursor.execute(
                    "SELECT pg_try_advisory_xact_lock(%s, %s)",
                    [table_lock_id(table), day.toordinal()],
                )
                if not cursor.fetchone()[0]:
                    transaction.set_rollback(True)
                    out(f"{day}: {table} already being recomputed, skipped")
                    return

            cursor.execute("DROP TABLE IF EXISTS day_tests")
            cursor.execute("DROP TABLE IF EXISTS platform_compatibles")
            cursor.execute(MATERIALIZE_DAY_TESTS, {"day": day})
            cursor.execute(MATERIALIZE_PLATFORM_COMPATIBLES)

            for table, insert in zip(tables, inserts, strict=True):
                cursor.execute(f"DELETE FROM {table} WHERE checkout_day = %s", [day])
                deleted += cursor.rowcount
                cursor.execute(insert, {"day": day})
                inserted += cursor.rowcount

            # No rows for a day that had them means pruned raw, keep the stale aggregate.
            if inserted == 0 and deleted > 0:
                transaction.set_rollback(True)
                out(f"{day}: raw data pruned, kept the {deleted} existing rows")
                return

        out(f"{day}: {inserted} rows written, {deleted} replaced")
