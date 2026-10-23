from django.core.management.base import BaseCommand
from django.db import connection

from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX
from kernelCI_app.helpers.logger import out

_DUMMY_LIKE = MAESTRO_DUMMY_BUILD_PREFIX.replace("_", "\\_")

# Every checkout of the same tree and commit counts into one tree_listing row.
_SAME_TREE = """
    {alias}.origin = c.origin
    AND {alias}.tree_name IS NOT DISTINCT FROM c.tree_name
    AND {alias}.git_repository_url IS NOT DISTINCT FROM c.git_repository_url
    AND {alias}.git_repository_branch IS NOT DISTINCT FROM c.git_repository_branch
    AND {alias}.git_commit_hash IS NOT DISTINCT FROM c.git_commit_hash
"""

_UPDATE = f"""
    UPDATE tree_listing tl
    SET
        build_pass = b.build_pass,
        build_failed = b.build_failed,
        build_inc = b.build_inc,
        boot_pass = t.boot_pass,
        boot_failed = t.boot_failed,
        boot_inc = t.boot_inc,
        test_pass = t.test_pass,
        test_failed = t.test_failed,
        test_inc = t.test_inc
    FROM checkouts c
    CROSS JOIN LATERAL (
        SELECT
            COUNT(*) FILTER (WHERE b.status = 'PASS') AS build_pass,
            COUNT(*) FILTER (WHERE b.status = 'FAIL') AS build_failed,
            COUNT(*) FILTER (
                WHERE b.status IS DISTINCT FROM 'PASS'
                  AND b.status IS DISTINCT FROM 'FAIL'
            ) AS build_inc
        FROM builds b
        JOIN checkouts bc ON bc.id = b.checkout_id
        WHERE {_SAME_TREE.format(alias="bc")}
          AND b.id NOT LIKE '{_DUMMY_LIKE}%%'
    ) b
    CROSS JOIN LATERAL (
        SELECT
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
        FROM (
            SELECT
                (t.path = 'boot' OR t.path LIKE 'boot.%%') IS TRUE AS is_boot,
                t.status
            FROM tests t
            JOIN builds tb ON tb.id = t.build_id
            JOIN checkouts tc ON tc.id = tb.checkout_id
            WHERE {_SAME_TREE.format(alias="tc")}
        ) tests
    ) t
    WHERE c.id = %(checkout_id)s
      AND {_SAME_TREE.format(alias="tl")}
"""


class Command(BaseCommand):
    help = (
        "Recompute tree_listing counts from builds and tests for one checkout. "
        "Stop process_pending_aggregations first; its additive writes race this."
    )

    def add_arguments(self, parser):
        parser.add_argument("--checkout-id", required=True)

    def handle(self, *args, **options):
        checkout_id = options["checkout_id"]
        with connection.cursor() as cursor:
            cursor.execute(_UPDATE, {"checkout_id": checkout_id})
            updated = cursor.rowcount
        out(f"checkout={checkout_id}: {updated} tree_listing rows recomputed")
