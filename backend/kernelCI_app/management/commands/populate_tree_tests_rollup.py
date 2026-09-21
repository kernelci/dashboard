import time
from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from kernelCI_app.helpers.logger import out
from kernelCI_app.management.commands.helpers.aggregation_helpers import (
    convert_test,
    simplify_status,
)
from kernelCI_app.management.commands.helpers.process_pending_helpers import (
    RollupKey,
    aggregate_tests_rollup,
    fetch_test_issues,
    get_rollup_key,
)
from kernelCI_app.models import (
    Builds,
    Checkouts,
    PendingTest,
    ProcessedListingItems,
    Tests,
)


def _chunks(iterator, chunk_size: int):
    """Yield chunks from an iterator."""
    chunk = []
    for item in iterator:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def _merge_rollup(
    accumulator: dict[RollupKey, dict], chunk_rollup: dict[RollupKey, dict]
) -> None:
    """Merge chunk rollup data into the accumulator."""
    for key, data in chunk_rollup.items():
        rollup_totals = accumulator.setdefault(
            key,
            {
                "pass_tests": 0,
                "fail_tests": 0,
                "skip_tests": 0,
                "error_tests": 0,
                "miss_tests": 0,
                "done_tests": 0,
                "null_tests": 0,
                "total_tests": 0,
            },
        )
        rollup_totals["pass_tests"] += data["pass_tests"]
        rollup_totals["fail_tests"] += data["fail_tests"]
        rollup_totals["skip_tests"] += data["skip_tests"]
        rollup_totals["error_tests"] += data["error_tests"]
        rollup_totals["miss_tests"] += data["miss_tests"]
        rollup_totals["done_tests"] += data["done_tests"]
        rollup_totals["null_tests"] += data["null_tests"]
        rollup_totals["total_tests"] += data["total_tests"]


class Command(BaseCommand):
    help = (
        "Recompute tree_tests_rollup and ProcessedListingItems from source data. "
        "Runbook: stop process_pending_aggregations before running, restart after. "
        "Running concurrently with the ingester will clobber its additive writes."
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--checkout-id",
            type=str,
            help="Process a single checkout by ID (errors if not found)",
        )
        parser.add_argument(
            "--since-days",
            type=int,
            help="Only process checkouts with start_time >= now - N days",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Process only the first N checkouts in iteration order",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=5000,
            help="Tests per chunk and issues IN-chunk size (default: 5000)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Read and aggregate, but skip all writes",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        checkout_id = options.get("checkout_id")
        since_days = options.get("since_days")
        limit = options.get("limit")
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]

        counts = {"ok": 0, "empty": 0, "failed": 0, "buckets": 0, "rows": 0}

        for checkout in self._iter_checkouts(
            checkout_id=checkout_id, since_days=since_days, limit=limit
        ):
            try:
                res = self._process_checkout(
                    checkout, batch_size=batch_size, dry_run=dry_run
                )
                counts[res["status"]] += 1
                counts["buckets"] += res["buckets"]
                counts["rows"] += res["rows"]
            except Exception as e:
                out(f"ERROR checkout={checkout.id}: {e}")
                counts["failed"] += 1

        out(
            f"Summary: ok={counts['ok']}, empty={counts['empty']}, "
            f"failed={counts['failed']}, buckets={counts['buckets']}, rows={counts['rows']}"
        )

    def _iter_checkouts(
        self, *, checkout_id: str | None, since_days: int | None, limit: int | None
    ):
        """Iterate over checkouts matching the filter criteria."""
        checkouts_qs = Checkouts.objects.order_by("-start_time", "-id")

        if since_days is not None:
            cutoff = timezone.now() - timedelta(days=since_days)
            checkouts_qs = checkouts_qs.filter(start_time__gte=cutoff)

        if checkout_id:
            checkouts_qs = checkouts_qs.filter(id=checkout_id)
            if not checkouts_qs.exists():
                raise CommandError(f"Checkout with id={checkout_id} not found")

        checkouts_qs = checkouts_qs[:limit]

        return checkouts_qs.iterator(chunk_size=100)

    def _process_checkout(
        self, checkout: Checkouts, *, batch_size: int, dry_run: bool
    ) -> dict[str, Any]:
        """Process a single checkout and return result metadata."""
        checkout_start = time.time()

        builds = (
            Builds.objects.filter(checkout_id=checkout.id)
            .select_related("checkout")
            .in_bulk(field_name="id")
        )

        if not builds:
            return {"status": "empty", "buckets": 0, "rows": 0}

        rollup_acc: dict[RollupKey, dict] = {}
        processed_rows: list[ProcessedListingItems] = []
        total_tests = 0

        tests_qs = Tests.objects.filter(build_id__in=builds.keys()).select_related(
            "build__checkout"
        )

        for test_chunk in _chunks(tests_qs.iterator(chunk_size=batch_size), batch_size):
            converted: list[PendingTest] = []
            test_ids: list[str] = []
            chunk_processed_rows: list[ProcessedListingItems] = []

            for t in test_chunk:
                converted.append(convert_test(t))
                test_ids.append(t.id)
                chunk_processed_rows.append(
                    ProcessedListingItems(
                        listing_item_key=get_rollup_key(t.id),
                        checkout_id=checkout.id,
                        status=simplify_status(t.status),
                    )
                )

            issues_map = fetch_test_issues(test_ids)
            chunk_rollup = aggregate_tests_rollup(converted, builds, issues_map)

            _merge_rollup(rollup_acc, chunk_rollup)

            processed_rows.extend(chunk_processed_rows)
            total_tests += len(test_chunk)

        if not processed_rows:
            return {"status": "empty", "buckets": 0, "rows": 0}

        if dry_run:
            out(
                f"DRY-RUN checkout={checkout.id} buckets={len(rollup_acc)} "
                f"tests={total_tests}"
            )
            return {"status": "ok", "buckets": len(rollup_acc), "rows": total_tests}

        with transaction.atomic():
            self._upsert_rollup_replace(rollup_acc)
            ProcessedListingItems.objects.bulk_create(
                processed_rows,
                update_conflicts=True,
                update_fields=["checkout_id", "status"],
                unique_fields=["listing_item_key"],
                batch_size=1000,
            )

        elapsed = time.time() - checkout_start
        out(
            f"checkout={checkout.id} buckets={len(rollup_acc)} tests={total_tests} "
            f"elapsed={elapsed:.3f}s"
        )

        return {"status": "ok", "buckets": len(rollup_acc), "rows": total_tests}

    def _upsert_rollup_replace(self, rollup_data: dict[RollupKey, dict]) -> None:
        """Upsert rollup data replacing existing rows counts."""
        if not rollup_data:
            return

        values = [{**key._asdict(), **data} for key, data in rollup_data.items()]

        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO tree_tests_rollup (
                    origin, tree_name, git_repository_branch, git_repository_url,
                    git_commit_hash, path_group, build_config_name, build_architecture,
                    build_compiler, hardware_key, test_platform, test_lab, test_origin,
                    issue_id, issue_version, issue_uncategorized, is_boot,
                    pass_tests, fail_tests, skip_tests, error_tests,
                    miss_tests, done_tests, null_tests, total_tests
                )
                VALUES (
                    %(origin)s, %(tree_name)s, %(git_repository_branch)s,
                    %(git_repository_url)s, %(git_commit_hash)s, %(path_group)s,
                    %(config)s, %(arch)s, %(compiler)s, %(hardware_key)s,
                    %(platform)s, %(lab)s, %(test_origin)s, %(issue_id)s,
                    %(issue_version)s, %(issue_uncategorized)s, %(is_boot)s,
                    %(pass_tests)s, %(fail_tests)s, %(skip_tests)s, %(error_tests)s,
                    %(miss_tests)s, %(done_tests)s, %(null_tests)s, %(total_tests)s
                )
                ON CONFLICT ON CONSTRAINT tree_tests_rollup_unique DO UPDATE SET
                    pass_tests = EXCLUDED.pass_tests,
                    fail_tests = EXCLUDED.fail_tests,
                    skip_tests = EXCLUDED.skip_tests,
                    error_tests = EXCLUDED.error_tests,
                    miss_tests = EXCLUDED.miss_tests,
                    done_tests = EXCLUDED.done_tests,
                    null_tests = EXCLUDED.null_tests,
                    total_tests = EXCLUDED.total_tests
                """,
                values,
            )
