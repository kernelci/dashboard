import time
from collections.abc import Iterator

from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction
from django.db.backends.utils import CursorWrapper

from kernelCI_app.constants.ingester import AUTOMATIC_LAB_FIELD, AUTOMATIC_LABS
from kernelCI_app.helpers.logger import out


def _real_lab_filter(misc_key: str) -> str:
    """Keep non-automatic labs only (`_real_lab`). Named param: pattern."""
    return f"""
        misc->>'{misc_key}' IS NOT NULL
        AND misc->>'{misc_key}' !~ %(pattern)s
        AND misc->>'{AUTOMATIC_LAB_FIELD}' IS NULL
    """


def _collect_lab_names(cur: CursorWrapper) -> list[str]:
    cur.execute(
        f"""
        SELECT DISTINCT lab FROM (
            SELECT misc->>'lab' AS lab FROM builds
            WHERE lab_id IS NULL
              AND {_real_lab_filter("lab")}
            UNION
            SELECT misc->>'runtime' AS lab FROM tests
            WHERE lab_id IS NULL
              AND {_real_lab_filter("runtime")}
        ) sub
        """,
        {"pattern": AUTOMATIC_LABS.pattern},
    )
    return [row[0] for row in cur.fetchall()]


def _ensure_labs(cur: CursorWrapper, lab_names: list[str]) -> None:
    cur.executemany(
        "INSERT INTO labs (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        [(name,) for name in lab_names],
    )
    transaction.commit()


def _stage_pending_ids(cur: CursorWrapper, table: str, misc_key: str) -> str:
    temp = f"_backfill_{table}_ids"
    cur.execute(f"DROP TABLE IF EXISTS {temp}")
    cur.execute(
        f"""
        CREATE TEMP TABLE {temp} AS
        SELECT id FROM {table}
        WHERE lab_id IS NULL
          AND {_real_lab_filter(misc_key)}
        """,
        {"pattern": AUTOMATIC_LABS.pattern},
    )
    return temp


def _count_pending(cur: CursorWrapper, temp: str) -> int:
    cur.execute(f"SELECT COUNT(*) FROM {temp}")
    return cur.fetchone()[0]


def _backfill_table(
    cur: CursorWrapper,
    table: str,
    misc_key: str,
    temp: str,
    batch_size: int,
) -> Iterator[int]:
    """Yield cumulative updated row count after each batch."""
    total = 0
    while True:
        cur.execute(
            f"""
            WITH batch AS (
                DELETE FROM {temp}
                WHERE id IN (SELECT id FROM {temp} LIMIT %s)
                RETURNING id
            ),
            updated_rows AS (
                UPDATE {table} AS target
                SET lab_id = lab.id
                FROM batch AS batch_row, labs AS lab
                WHERE target.id = batch_row.id
                  AND target.misc->>%s = lab.name
                RETURNING target.id
            )
            SELECT
                (SELECT COUNT(*) FROM batch),
                (SELECT COUNT(*) FROM updated_rows)
            """,
            [batch_size, misc_key],
        )
        batch_count, updated = cur.fetchone()
        if batch_count == 0:
            return
        total += updated
        transaction.commit()
        yield total


class Command(BaseCommand):
    help = (
        "Backfill lab_id FK on builds and tests from JSONB misc fields "
        "(builds: misc->>'lab', tests: misc->>'runtime'). "
        "Skips automatic labs (shell/k8s* or misc.automatic_lab); leaves lab_id NULL."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50_000,
            help="Rows per UPDATE batch (default: 50000)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Stage pending ids into a temp table and print counts, "
                "but do not insert labs or update lab_id"
            ),
        )

    def handle(self, *args, **options) -> None:
        batch_size: int = options["batch_size"]
        dry_run: bool = options["dry_run"]

        if batch_size < 1:
            raise CommandError("--batch-size must be >= 1")

        with connections["default"].cursor() as cur:
            if not dry_run:
                out("Collecting distinct lab names from JSONB...")
                lab_names = _collect_lab_names(cur)
                out(f"  Found {len(lab_names)} distinct lab names")
                if lab_names:
                    out("Inserting missing lab names into labs table...")
                    _ensure_labs(cur, lab_names)

            for table, misc_key in (("builds", "lab"), ("tests", "runtime")):
                out(f"Staging {table} ids...")
                temp = _stage_pending_ids(cur, table, misc_key)
                pending_count = _count_pending(cur, temp)
                out(f"{table.capitalize()} to backfill: {pending_count}")

                if not pending_count or dry_run:
                    continue

                started_at = time.time()
                for total in _backfill_table(cur, table, misc_key, temp, batch_size):
                    out(
                        f"  {table}: {total}/{pending_count} "
                        f"({time.time() - started_at:.1f}s)"
                    )

        out("Dry run complete, no lab_id changes made." if dry_run else "Done.")
