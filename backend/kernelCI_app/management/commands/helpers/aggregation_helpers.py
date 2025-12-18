import time
from typing import Sequence


from django.db import connections
from kernelCI_app.helpers.logger import out
from kernelCI_app.models import (
    Checkouts,
    PendingTest,
    PendingBuilds,
    StatusChoices,
    SimplifiedStatusChoices,
    Tests,
    Builds,
)
from kernelCI_app.utils import is_boot
from typing import Optional


def simplify_status(status: Optional[StatusChoices]) -> SimplifiedStatusChoices:
    if status == StatusChoices.PASS:
        return SimplifiedStatusChoices.PASS
    elif status == StatusChoices.FAIL:
        return SimplifiedStatusChoices.FAIL
    else:
        return SimplifiedStatusChoices.INCONCLUSIVE


def convert_build(b: Builds) -> PendingBuilds:
    return PendingBuilds(
        build_id=b.id,
        origin=b.origin,
        checkout_id=b.checkout_id,
        status=simplify_status(b.status),
    )


def convert_test(t: Tests) -> PendingTest:
    return PendingTest(
        test_id=t.id,
        origin=t.origin,
        platform=t.environment_misc.get("platform"),
        compatible=t.environment_compatible,
        build_id=t.build_id,
        status=simplify_status(t.status),
        is_boot=is_boot(t.path) if t.path else False,
    )


def update_tree_listing(checkouts_instances: Sequence[Checkouts]):
    """
    Whenever a checkout updates the latest_checkout table,
    we update the tree_listing table, zeroing the counts.

    We should also remove the old tree row from the listing
    """

    t0 = time.time()
    checkout_values = [
        (
            checkout.id,
            checkout.origin,
            checkout.tree_name,
            checkout.git_repository_url,
            checkout.git_repository_branch,
            checkout.git_commit_hash,
            checkout.git_commit_name,
            checkout.git_commit_tags,
            checkout.start_time,
        )
        for checkout in checkouts_instances
    ]

    with connections["default"].cursor() as cursor:
        # Set values as 0 when inserting a new tree and update as 0 when tree already exists
        cursor.executemany(
            """
            INSERT INTO tree_listing (
                checkout_id, origin, tree_name,
                git_repository_url, git_repository_branch, git_commit_hash,
                git_commit_name, git_commit_tags, start_time,
                build_pass, build_failed, build_inc,
                boot_pass, boot_failed, boot_inc,
                test_pass, test_failed, test_inc
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            ON CONFLICT (origin, tree_name, git_repository_url, git_repository_branch)
            DO UPDATE SET
                checkout_id = EXCLUDED.checkout_id,
                git_commit_hash = EXCLUDED.git_commit_hash,
                git_commit_name = EXCLUDED.git_commit_name,
                git_commit_tags = EXCLUDED.git_commit_tags,
                start_time = EXCLUDED.start_time,
                build_pass = 0,
                build_failed = 0,
                build_inc = 0,
                boot_pass = 0,
                boot_failed = 0,
                boot_inc = 0,
                test_pass = 0,
                test_failed = 0,
                test_inc = 0
            WHERE tree_listing.start_time < EXCLUDED.start_time
            """,
            checkout_values,
        )
    out(
        f"upserted {len(checkouts_instances)} tree_listing trees in {time.time() - t0:.3f}s"
    )


def aggregate_checkouts(checkouts_instances: Sequence[Checkouts]) -> None:
    """
    Insert checkouts on latest_checkouts table,
    maintaining only the latest ones for each
    (origin, tree_name, git_repository_url, git_repository_branch) combination
    """
    t0 = time.time()
    values = [
        (
            checkout.id,
            checkout.origin,
            checkout.tree_name,
            checkout.git_repository_url,
            checkout.git_repository_branch,
            checkout.start_time,
        )
        for checkout in checkouts_instances
    ]

    if len(values) > 0:
        with connections["default"].cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO latest_checkout (
                    checkout_id, origin, tree_name,
                    git_repository_url, git_repository_branch, start_time
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (origin, tree_name, git_repository_url, git_repository_branch)
                DO UPDATE SET
                    start_time = EXCLUDED.start_time,
                    checkout_id = EXCLUDED.checkout_id
                WHERE latest_checkout.start_time < EXCLUDED.start_time
                """,
                values,
            )
        out(f"inserted {len(checkouts_instances)} checkouts in {time.time() - t0:.3f}s")


def aggregate_tests(
    tests_instances: Sequence[Tests],
) -> None:
    """Insert tests data on pending_tests table to be processed later"""
    t0 = time.time()
    pending_tests = (
        convert_test(test)
        for test in tests_instances
        if test.environment_misc and test.environment_misc.get("platform") is not None
    )

    if pending_tests:
        pending_tests_inserted = PendingTest.objects.bulk_create(
            pending_tests,
            ignore_conflicts=True,
        )
        out(
            f"bulk_create pending_tests: n={len(pending_tests_inserted)} in {time.time() - t0:.3f}s"
        )


def aggregate_builds(
    build_instances: Sequence[Builds],
) -> None:
    """Insert builds data on pending_builds table to be processed later"""
    t0 = time.time()
    pending_builds = (convert_build(build) for build in build_instances)

    if pending_builds:
        pending_builds_inserted = PendingBuilds.objects.bulk_create(
            pending_builds,
            ignore_conflicts=True,
        )
        out(
            f"bulk_create pending_builds: n={len(pending_builds_inserted)} in {time.time() - t0:.3f}s"
        )


def aggregate_checkouts_and_pendings(
    checkouts_instances: Sequence[Checkouts],
    tests_instances: Sequence[Tests],
    build_instances: Sequence[Builds],
) -> None:
    aggregate_checkouts(checkouts_instances)
    update_tree_listing(checkouts_instances)
    aggregate_tests(tests_instances)
    aggregate_builds(build_instances)
