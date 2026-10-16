import hashlib
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX
from kernelCI_app.helpers.logger import out

_DUMMY_LIKE = MAESTRO_DUMMY_BUILD_PREFIX.replace("_", "\\_")

_INSERT = f"""
    INSERT INTO lab_daily (
        day, origin, lab_id,
        build_pass, build_failed, build_inc,
        boot_pass, boot_failed, boot_inc,
        test_pass, test_failed, test_inc
    )
    WITH day_builds AS (
        SELECT
            origin,
            lab_id,
            COUNT(*) FILTER (WHERE status = 'PASS') AS build_pass,
            COUNT(*) FILTER (WHERE status = 'FAIL') AS build_failed,
            COUNT(*) FILTER (
                WHERE status IS DISTINCT FROM 'PASS'
                  AND status IS DISTINCT FROM 'FAIL'
            ) AS build_inc
        FROM builds
        WHERE lab_id IS NOT NULL
          AND start_time >= %(day)s::timestamp AT TIME ZONE 'UTC'
          AND start_time < (%(day)s::date + 1)::timestamp AT TIME ZONE 'UTC'
          AND id NOT LIKE '{_DUMMY_LIKE}%%'
        GROUP BY origin, lab_id
    ),
    day_tests AS (
        SELECT
            origin,
            lab_id,
            (path = 'boot' OR path LIKE 'boot.%%') AS is_boot,
            status
        FROM tests
        WHERE lab_id IS NOT NULL
          AND path IS NOT NULL
          AND start_time >= %(day)s::timestamp AT TIME ZONE 'UTC'
          AND start_time < (%(day)s::date + 1)::timestamp AT TIME ZONE 'UTC'
    ),
    counted_tests AS (
        SELECT
            origin,
            lab_id,
            COUNT(*) FILTER (WHERE is_boot AND status = 'PASS') AS boot_pass,
            COUNT(*) FILTER (WHERE is_boot AND status = 'FAIL') AS boot_failed,
            COUNT(*) FILTER (
                WHERE is_boot
                  AND status IS DISTINCT FROM 'PASS'
                  AND status IS DISTINCT FROM 'FAIL'
            ) AS boot_inc,
            COUNT(*) FILTER (WHERE NOT is_boot AND status = 'PASS') AS test_pass,
            COUNT(*) FILTER (WHERE NOT is_boot AND status = 'FAIL') AS test_failed,
            COUNT(*) FILTER (
                WHERE NOT is_boot
                  AND status IS DISTINCT FROM 'PASS'
                  AND status IS DISTINCT FROM 'FAIL'
            ) AS test_inc
        FROM day_tests
        GROUP BY origin, lab_id
    )
    SELECT
        %(day)s::date AS day,
        COALESCE(day_builds.origin, counted_tests.origin) AS origin,
        COALESCE(day_builds.lab_id, counted_tests.lab_id) AS lab_id,
        COALESCE(day_builds.build_pass, 0) AS build_pass,
        COALESCE(day_builds.build_failed, 0) AS build_failed,
        COALESCE(day_builds.build_inc, 0) AS build_inc,
        COALESCE(counted_tests.boot_pass, 0) AS boot_pass,
        COALESCE(counted_tests.boot_failed, 0) AS boot_failed,
        COALESCE(counted_tests.boot_inc, 0) AS boot_inc,
        COALESCE(counted_tests.test_pass, 0) AS test_pass,
        COALESCE(counted_tests.test_failed, 0) AS test_failed,
        COALESCE(counted_tests.test_inc, 0) AS test_inc
    FROM day_builds
    FULL JOIN counted_tests USING (origin, lab_id)
"""


def lock_key(table: str) -> int:
    return int.from_bytes(hashlib.sha256(table.encode()).digest()[:4]) % 2**31


class Command(BaseCommand):
    help = "Recompute lab_daily from builds and tests for one or more UTC days."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=1,
            help="Days to recompute back from today, including today",
        )
        parser.add_argument(
            "--day",
            type=date.fromisoformat,
            help="Recompute a single day (YYYY-MM-DD) instead of the recent window",
        )

    def handle(self, *args, **options):
        if options["days"] < 1:
            raise CommandError("--days must be >= 1")

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
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_try_advisory_xact_lock(%s, %s)",
                [lock_key("lab_daily"), day.toordinal()],
            )
            if not cursor.fetchone()[0]:
                transaction.set_rollback(True)
                out(f"{day}: lab_daily already being recomputed, skipped")
                return

            cursor.execute("DELETE FROM lab_daily WHERE day = %s", [day])
            deleted = cursor.rowcount
            cursor.execute(_INSERT, {"day": day})
            inserted = cursor.rowcount

            if inserted == 0 and deleted > 0:
                transaction.set_rollback(True)
                out(f"{day}: raw data pruned, kept the {deleted} existing rows")
                return

        out(f"{day}: {inserted} rows written, {deleted} replaced")
