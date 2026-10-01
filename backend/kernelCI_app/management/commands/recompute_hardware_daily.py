"""Rebuild hardware_daily_* for a UTC checkout day from raw checkouts/builds/tests.

Idempotent: DELETE + INSERT. If raw is gone but aggregates exist, roll back.
"""

import hashlib
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX
from kernelCI_app.helpers.logger import out


def lock_key(table: str) -> int:
    return int.from_bytes(hashlib.sha256(table.encode()).digest()[:4]) % 2**31


# PASS/FAIL are verdicts; NULL, MISS, SKIP, ERROR, DONE all land in inc.
_BUCKET = (
    "CASE WHEN {col} = 'PASS' THEN 'pass'"
    " WHEN {col} = 'FAIL' THEN 'failed' ELSE 'inc' END"
)

# Half-open UTC day so the start_time index is usable.
DAY_TESTS = f"""
    SELECT
        c.id AS checkout_id,
        c.origin AS checkout_origin,
        t.origin,
        COALESCE(NULLIF(t.misc ->> 'runtime', ''), t.origin) AS lab,
        t.environment_misc ->> 'platform' AS platform,
        t.environment_compatible AS compatibles,
        COALESCE(t.path = 'boot' OR t.path LIKE 'boot.%%', false) AS is_boot,
        {_BUCKET.format(col="t.status")} AS result,
        b.id AS build_id,
        b.origin AS build_origin,
        COALESCE(
            NULLIF(b.misc ->> 'lab', ''), NULLIF(b.misc ->> 'runtime', ''), b.origin
        ) AS build_lab,
        {_BUCKET.format(col="b.status")} AS build_result
    FROM tests t
    JOIN builds b ON b.id = t.build_id
    JOIN checkouts c ON c.id = b.checkout_id
    WHERE c.start_time >= %(day)s::timestamp AT TIME ZONE 'UTC'
      AND c.start_time < (%(day)s::date + 1)::timestamp AT TIME ZONE 'UTC'
      AND t.environment_misc ->> 'platform' IS NOT NULL
"""

# One label per platform: longest compatible chain, so labs cannot list the board twice.
PLATFORM_COMPATIBLES = """
    SELECT DISTINCT ON (checkout_id, platform) checkout_id, platform, compatibles
    FROM day_tests
    WHERE compatibles IS NOT NULL
    ORDER BY checkout_id, platform, cardinality(compatibles) DESC, compatibles
"""

INSERT_TESTS = """
INSERT INTO hardware_daily_tests (
    checkout_day, checkout_id, checkout_origin, test_origin, test_lab, platform,
    compatibles, boot_pass, boot_failed, boot_inc, test_pass, test_failed, test_inc
)
WITH counted AS (
    SELECT
        checkout_id,
        checkout_origin,
        origin,
        lab,
        platform,
        count(*) FILTER (WHERE is_boot AND result = 'pass') AS boot_pass,
        count(*) FILTER (WHERE is_boot AND result = 'failed') AS boot_failed,
        count(*) FILTER (WHERE is_boot AND result = 'inc') AS boot_inc,
        count(*) FILTER (WHERE NOT is_boot AND result = 'pass') AS test_pass,
        count(*) FILTER (WHERE NOT is_boot AND result = 'failed') AS test_failed,
        count(*) FILTER (WHERE NOT is_boot AND result = 'inc') AS test_inc
    FROM day_tests
    GROUP BY checkout_id, checkout_origin, origin, lab, platform
)
SELECT
    %(day)s,
    c.checkout_id,
    c.checkout_origin,
    c.origin,
    c.lab,
    c.platform,
    pc.compatibles,
    c.boot_pass, c.boot_failed, c.boot_inc, c.test_pass, c.test_failed, c.test_inc
FROM counted c
LEFT JOIN platform_compatibles pc USING (checkout_id, platform)
"""

# Builds have no platform; attach them to every platform they tested, but DISTINCT so
# a build is not counted once per test (or per test lab).
INSERT_BUILDS = f"""
INSERT INTO hardware_daily_builds (
    checkout_day, checkout_id, checkout_origin, build_origin, build_lab, platform,
    compatibles, build_pass, build_failed, build_inc
)
WITH day_builds AS (
    SELECT DISTINCT checkout_id, checkout_origin, build_id, build_origin, build_lab,
                    platform, build_result
    FROM day_tests
    WHERE build_id NOT LIKE '{MAESTRO_DUMMY_BUILD_PREFIX}%%'
),
counted AS (
    SELECT
        checkout_id,
        checkout_origin,
        build_origin,
        build_lab,
        platform,
        count(*) FILTER (WHERE build_result = 'pass') AS build_pass,
        count(*) FILTER (WHERE build_result = 'failed') AS build_failed,
        count(*) FILTER (WHERE build_result = 'inc') AS build_inc
    FROM day_builds
    GROUP BY checkout_id, checkout_origin, build_origin, build_lab, platform
)
SELECT
    %(day)s,
    c.checkout_id,
    c.checkout_origin,
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

    def handle(self, *args, **options):
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
            # Cron-only txn: keep the day's sort/hash in memory.
            cursor.execute("SET LOCAL work_mem = '128MB'")

            for table in tables:
                cursor.execute(
                    "SELECT pg_try_advisory_xact_lock(%s, %s)",
                    [lock_key(table), day.toordinal()],
                )
                if not cursor.fetchone()[0]:
                    transaction.set_rollback(True)
                    out(f"{day}: {table} already being recomputed, skipped")
                    return

            # Nested pytest transactions never COMMIT, so ON COMMIT DROP never fires.
            cursor.execute("DROP TABLE IF EXISTS day_tests")
            cursor.execute("DROP TABLE IF EXISTS platform_compatibles")
            cursor.execute(
                f"CREATE TEMP TABLE day_tests ON COMMIT DROP AS\n{DAY_TESTS}",
                {"day": day},
            )
            # Temp tables have no stats; ANALYZE so the planner hashes instead of sorting.
            cursor.execute("ANALYZE day_tests")
            cursor.execute(
                f"CREATE TEMP TABLE platform_compatibles ON COMMIT DROP AS\n"
                f"{PLATFORM_COMPATIBLES}"
            )

            for table, insert in zip(tables, inserts, strict=True):
                cursor.execute(f"DELETE FROM {table} WHERE checkout_day = %s", [day])
                deleted += cursor.rowcount
                cursor.execute(insert, {"day": day})
                inserted += cursor.rowcount

            if inserted == 0 and deleted > 0:
                transaction.set_rollback(True)
                out(f"{day}: raw data pruned, kept the {deleted} existing rows")
                return

        out(f"{day}: {inserted} rows written, {deleted} replaced")
