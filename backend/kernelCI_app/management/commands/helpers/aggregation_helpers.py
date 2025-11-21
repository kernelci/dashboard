from typing import Sequence


from django.db import connection
from kernelCI_app.models import (
    Checkouts,
    PendingTest,
    StatusChoices,
    SimplifiedStatusChoices,
    Tests,
)
from kernelCI_app.utils import is_boot


def simplify_status(status: StatusChoices) -> SimplifiedStatusChoices:
    if status == StatusChoices.PASS:
        return SimplifiedStatusChoices.PASS
    elif status == StatusChoices.FAIL:
        return SimplifiedStatusChoices.FAIL
    else:
        return SimplifiedStatusChoices.INCOMPLETE


def convert_test(t: Tests) -> PendingTest:
    return PendingTest(
        test_id=t.id,
        origin=t.origin,
        platform=t.environment_misc.get("platform"),
        compatible=t.environment_compatible,
        build_id=t.build_id,
        status=(
            simplify_status(t.status)
            if t.status
            else SimplifiedStatusChoices.INCOMPLETE
        ),
        is_boot=is_boot(t.path) if t.path else False,
    )


def aggregate_checkouts(checkouts_instances: Sequence[Checkouts]) -> None:
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

    with connection.cursor() as cursor:
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


def aggregate_tests(
    tests_instances: Sequence[Tests],
) -> None:
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
        print(f"inserted {len(pending_tests_inserted)} pending tests")


def aggregate_checkouts_and_tests(
    checkouts_instances: Sequence[Checkouts],
    tests_instances: Sequence[Tests],
) -> None:
    aggregate_checkouts(checkouts_instances)
    aggregate_tests(tests_instances)
