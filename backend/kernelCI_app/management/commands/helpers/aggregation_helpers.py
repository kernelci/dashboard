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
    if status is None:
        return None
    elif status == StatusChoices.PASS:
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
        platform=t.environment_misc.get("platform") if t.environment_misc else None,
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
    if not checkouts_instances:
        return

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
        # Set values as 0 when inserting a new tree
        # and only updates basic information when tree already exists
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
            ON CONFLICT (origin, tree_name, git_repository_url, git_repository_branch, git_commit_hash)
            DO UPDATE SET
                checkout_id = EXCLUDED.checkout_id,
                git_commit_hash = EXCLUDED.git_commit_hash,
                git_commit_name = EXCLUDED.git_commit_name,
                git_commit_tags = EXCLUDED.git_commit_tags,
                start_time = EXCLUDED.start_time
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
    pending_tests = (convert_test(test) for test in tests_instances)
    values = [
        (
            test.test_id,
            test.origin,
            test.platform,
            test.compatible,
            test.build_id,
            test.status,
            test.is_boot,
        )
        for test in pending_tests
    ]

    if pending_tests:
        query = """
            INSERT INTO pending_test (
                test_id, origin, platform, compatible,
                build_id, status, is_boot
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (test_id)
            DO UPDATE SET
                platform = COALESCE(pending_test.platform, EXCLUDED.platform),
                compatible = COALESCE(pending_test.compatible, EXCLUDED.compatible),
                status = COALESCE(pending_test.status, EXCLUDED.status)
        """

        with connections["default"].cursor() as cursor:
            cursor.executemany(query, values)
        out(f"bulk_create pending_tests in {time.time() - t0:.3f}s")


def aggregate_builds(
    build_instances: Sequence[Builds],
) -> None:
    """Insert builds data on pending_builds table to be processed later"""
    t0 = time.time()
    pending_builds = (convert_build(build) for build in build_instances)
    values = [
        (
            build.build_id,
            build.origin,
            build.checkout_id,
            build.status,
        )
        for build in pending_builds
    ]

    if pending_builds:
        query = """
            INSERT INTO pending_builds (
                build_id, origin, checkout_id, status
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT (build_id)
            DO UPDATE SET
                status = COALESCE(pending_builds.status, EXCLUDED.status)
        """
        with connections["default"].cursor() as cursor:
            cursor.executemany(query, values)
        out(f"bulk_create pending_builds in {time.time() - t0:.3f}s")


def aggregate_checkouts_and_pendings(
    checkouts_instances: Sequence[Checkouts],
    tests_instances: Sequence[Tests],
    build_instances: Sequence[Builds],
) -> None:
    aggregate_checkouts(checkouts_instances)
    update_tree_listing(checkouts_instances)
    aggregate_tests(tests_instances)
    aggregate_builds(build_instances)
