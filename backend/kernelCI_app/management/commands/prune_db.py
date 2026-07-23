"""
Management command to prune old builds, tests and checkouts.

Removes checkouts, builds and tests older than a given age. To keep referential
integrity, deletion cascades manually (models use DO_NOTHING): a removed
checkout drags its builds, and a removed build drags its tests, even when those
children are newer than the cutoff.

Rows linked to an incident (an issue) are kept by default, together with their
ancestors so nothing is orphaned; pass --skip-issue-protection to prune them too.

Only checkouts, builds and tests are touched. Aggregate and derived tables (e.g.
tree_tests_rollup, hardware_status, latest_checkout) are left untouched and must
be cleaned up separately.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from kernelCI_app.management.commands.helpers.intervals import parse_interval

# Strict parent-before-child order: a checkout owns builds, a build owns tests.
PRUNABLE_TABLES = ("checkouts", "builds", "tests")


class Command(BaseCommand):
    help = "Prune checkouts, builds and tests older than a given age"

    def add_arguments(self, parser):
        parser.add_argument(
            "--older-than",
            type=str,
            required=True,
            help="Delete rows older than this age ('x days' or 'x hours' format, "
            "e.g. '30 days')",
        )
        parser.add_argument(
            "--origins",
            type=lambda s: [origin.strip() for origin in s.split(",")],
            default=[],
            help="Limit age-based pruning to specific origins (comma-separated). "
            "Children of pruned parents are removed regardless of origin. "
            "If not provided, any origin is considered.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip the confirmation prompt and delete right away",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10000,
            help="Number of rows to delete per batch (default: 10000)",
        )
        parser.add_argument(
            "--tables",
            type=lambda s: [t.strip() for t in s.split(",")],
            default=list(PRUNABLE_TABLES),
            help="Limit pruning to specific tables (comma-separated: "
            f"{', '.join(PRUNABLE_TABLES)}). Only the listed tables are deleted; "
            "unlisted child tables are left untouched, so selecting a parent without "
            "its children (e.g. only 'checkouts') can leave orphans. Default: all.",
        )
        parser.add_argument(
            "--skip-issue-protection",
            action="store_true",
            help="Prune builds and tests linked to issues (default: keep rows with "
            "an associated incident)",
        )

    def handle(self, *args, **options):
        try:
            cutoff = parse_interval(options["older_than"])
        except ValueError as e:
            raise CommandError(str(e)) from e

        if options["batch_size"] < 1:
            raise CommandError(
                f"--batch-size must be at least 1 (got {options['batch_size']}). "
                "It sets how many rows are deleted per batch, so it needs to be a "
                "positive number."
            )

        unknown_tables = [t for t in options["tables"] if t not in PRUNABLE_TABLES]
        if unknown_tables:
            raise CommandError(
                f"Unknown table(s): {', '.join(unknown_tables)}. "
                f"Valid options are: {', '.join(PRUNABLE_TABLES)}."
            )
        selected_tables = [t for t in PRUNABLE_TABLES if t in options["tables"]]
        protect_incidents = not options["skip_issue_protection"]

        dry_run = options["dry_run"]
        origins = options["origins"]

        params = {"cutoff": cutoff}
        origins_condition = ""
        if origins:
            params["origins"] = origins
            origins_condition = "AND origin = ANY(%(origins)s)"

        where_clauses = self._build_where_clauses(
            origins_condition, protect_incidents, selected_tables
        )
        temp_tables = {t: f"prune_{t}" for t in selected_tables}

        with connections["default"].cursor() as cursor:
            try:
                # Snapshot ids while parents still exist, so child predicates can
                # resolve them. Do all tables before deleting anything.
                for table in selected_tables:
                    self._materialize(
                        cursor, table, temp_tables[table], where_clauses[table], params
                    )

                counts = {
                    t: self._count(cursor, temp_tables[t]) for t in selected_tables
                }
                total = sum(counts.values())

                lines = [f"Rows older than {cutoff.isoformat()}:"]
                lines += [f"* {t}:\t{counts[t]:>8}" for t in selected_tables]
                lines += ["----------------------", f"* total:\t{total:>8}"]
                lines.append(
                    "Note: counts include children cascaded from pruned parents."
                )
                if protect_incidents:
                    lines.append("Note: rows linked to an incident are kept.")
                self.stdout.write("\n".join(lines))

                if total == 0:
                    self.stdout.write(self.style.SUCCESS("Nothing to prune."))
                    return

                if dry_run:
                    self.stderr.write(
                        self.style.WARNING(
                            "[DRY RUN] No rows deleted. Run without --dry-run to "
                            "execute."
                        )
                    )
                    return

                if not options["yes"]:
                    try:
                        answer = input("Delete these rows? [y/N] ").strip().lower()
                    except EOFError:
                        answer = ""
                    if answer not in ("y", "yes"):
                        self.stdout.write("Aborted.")
                        return

                # Delete child-first (reverse of PRUNABLE_TABLES order): each batch
                # commits on its own, so a crash mid-run leaves children already gone
                # before their parents, never the reverse. Reordering this would risk
                # orphans.
                deleted = 0
                for table in reversed(selected_tables):
                    deleted += self._batch_delete(
                        cursor, table, temp_tables[table], options["batch_size"]
                    )

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully pruned {deleted} rows.")
                )
            finally:
                for temp_table in temp_tables.values():
                    cursor.execute(f'DROP TABLE IF EXISTS "{temp_table}"')

    def _build_where_clauses(
        self, origins_condition, protect_incidents, selected_tables
    ):
        """Build the per-table WHERE clauses, chaining the cascade so each child
        matches when its selected parent is doomed, and appending incident protection
        when enabled."""
        age = f"_timestamp < %(cutoff)s {origins_condition}"

        # A row tied to an incident is protected, along with the ancestors that would
        # otherwise be orphaned: a build is protected when it (or one of its tests) has
        # an incident, and a checkout when one of its builds is protected.
        incident_tests = "SELECT test_id FROM incidents WHERE test_id IS NOT NULL"
        incident_builds = (
            "SELECT build_id FROM incidents WHERE build_id IS NOT NULL "
            f"UNION SELECT build_id FROM tests WHERE id IN ({incident_tests})"
        )
        exclusion = (
            {
                "tests": f" AND id NOT IN ({incident_tests})",
                "builds": f" AND id NOT IN ({incident_builds})",
                "checkouts": (
                    " AND id NOT IN "
                    f"(SELECT checkout_id FROM builds WHERE id IN ({incident_builds}))"
                ),
            }
            if protect_incidents
            else {}
        )

        checkout_where = age + exclusion.get("checkouts", "")

        build_terms = [f"({age})"]
        if "checkouts" in selected_tables:
            build_terms.append(
                f"checkout_id IN (SELECT id FROM checkouts WHERE {checkout_where})"
            )
        build_where = "(" + " OR ".join(build_terms) + ")" + exclusion.get("builds", "")

        test_terms = [f"({age})"]
        if "builds" in selected_tables:
            test_terms.append(
                f"build_id IN (SELECT id FROM builds WHERE {build_where})"
            )
        test_where = "(" + " OR ".join(test_terms) + ")" + exclusion.get("tests", "")

        return {
            "checkouts": checkout_where,
            "builds": build_where,
            "tests": test_where,
        }

    def _materialize(self, cursor, table, temp_table, where, params):
        """Snapshot the doomed ids into a temp table so the nested predicate runs
        once instead of per batch."""
        cursor.execute(f'DROP TABLE IF EXISTS "{temp_table}"')
        cursor.execute(
            f'CREATE TEMP TABLE "{temp_table}" AS '
            f'SELECT id FROM "{table}" WHERE {where}',
            params,
        )

    def _count(self, cursor, temp_table):
        cursor.execute(f'SELECT COUNT(*) FROM "{temp_table}"')
        return cursor.fetchone()[0]

    def _batch_delete(self, cursor, table, temp_table, batch_size):
        sql = (
            f"WITH batch AS ("
            f'DELETE FROM "{temp_table}" WHERE id IN '
            f'(SELECT id FROM "{temp_table}" LIMIT %(batch_size)s) RETURNING id'
            f') DELETE FROM "{table}" WHERE id IN (SELECT id FROM batch)'
        )
        deleted_total = 0
        while True:
            cursor.execute(sql, {"batch_size": batch_size})
            deleted = cursor.rowcount
            if deleted == 0:
                break
            deleted_total += deleted
            self.stdout.write(f"Deleted {table}(n={deleted}) total={deleted_total}")
        return deleted_total
