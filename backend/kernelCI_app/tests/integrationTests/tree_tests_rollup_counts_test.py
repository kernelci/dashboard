"""Integration tests for the populate_tree_tests_rollup management command."""

import pytest
from django.core.management import call_command

from kernelCI_app.models import Labs, ProcessedListingItems, TreeTestsRollup
from kernelCI_app.tests.factories import (
    BuildFactory,
    CheckoutFactory,
    IncidentFactory,
    IssueFactory,
    TestFactory,
)

COUNTERS = (
    "pass_tests",
    "fail_tests",
    "skip_tests",
    "error_tests",
    "miss_tests",
    "done_tests",
    "null_tests",
    "total_tests",
)


def tally(**counts: int) -> dict[str, int]:
    row = {name: 0 for name in COUNTERS}
    row.update(counts)
    row["total_tests"] = sum(row[name] for name in COUNTERS if name != "total_tests")
    return row


@pytest.mark.django_db
def test_rollup_counts_one_checkout_from_raw_tests():
    lab = Labs.objects.create(name="lab-a")
    checkout = CheckoutFactory(
        id="rollup_checkout",
        origin="maestro",
        tree_name="mainline",
        git_repository_branch="master",
        git_repository_url="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
        git_commit_hash="abc123def456",
    )
    other = CheckoutFactory(id="rollup_other_checkout")
    build = BuildFactory(
        checkout=checkout,
        architecture="arm64",
        compiler="gcc-12",
        config_name="defconfig",
    )

    def add(path, status, **kwargs):
        return TestFactory(
            build=build,
            origin="maestro",
            path=path,
            status=status,
            lab=kwargs.pop("lab", lab),
            environment_misc=kwargs.pop("environment_misc", {"platform": "board"}),
            environment_compatible=kwargs.pop(
                "environment_compatible", ["board", "vendor,soc"]
            ),
            misc=kwargs.pop("misc", None),
            **kwargs,
        )

    issued = add("baseline.ktap", "FAIL")
    seeded = [
        add("boot", "PASS"),
        add("boot.nfs", "FAIL"),
        add("bootrr.probe", "PASS"),
        add("baseline.login", "PASS"),
        add("baseline.dmesg", "SKIP"),
        add("baseline.null", None),
        issued,
        add(None, "PASS"),
        add(
            "platform.case",
            "PASS",
            environment_misc={"platform": "qemu"},
            environment_compatible=None,
        ),
        add(
            "runtime.check",
            "PASS",
            lab=None,
            misc={"runtime": "lab-from-misc"},
        ),
    ]
    TestFactory(
        build=BuildFactory(checkout=other), path="baseline.login", status="PASS"
    )

    issue = IssueFactory(id="issue_rollup", version=3, origin="maestro")
    IncidentFactory(
        issue=issue,
        test=issued,
        build=build,
        origin="maestro",
        issue_version=3,
    )

    expected = {
        ("boot", True, None, False, "board", "lab-a", "board"): tally(pass_tests=1),
        ("boot", True, None, True, "board", "lab-a", "board"): tally(fail_tests=1),
        ("bootrr", False, None, False, "board", "lab-a", "board"): tally(pass_tests=1),
        ("baseline", False, None, False, "board", "lab-a", "board"): tally(
            pass_tests=1,
            skip_tests=1,
            null_tests=1,
        ),
        ("baseline", False, "issue_rollup", False, "board", "lab-a", "board"): tally(
            fail_tests=1
        ),
        ("-", False, None, False, "board", "lab-a", "board"): tally(pass_tests=1),
        ("platform", False, None, False, "qemu", "lab-a", "qemu"): tally(pass_tests=1),
        ("runtime", False, None, False, "board", "lab-from-misc", "board"): tally(
            pass_tests=1
        ),
    }

    call_command("populate_tree_tests_rollup", checkout_id=checkout.id)
    _assert_rollup(expected)
    assert ProcessedListingItems.objects.filter(checkout_id=checkout.id).count() == len(
        seeded
    )
    issued_row = TreeTestsRollup.objects.get(issue_id="issue_rollup")
    assert issued_row.issue_version == 3

    call_command("populate_tree_tests_rollup", checkout_id=checkout.id)
    _assert_rollup(expected)
    assert ProcessedListingItems.objects.filter(checkout_id=checkout.id).count() == len(
        seeded
    )


def _assert_rollup(expected: dict) -> None:
    rows = list(TreeTestsRollup.objects.all())
    for row in rows:
        assert row.origin == "maestro"
        assert row.tree_name == "mainline"
        assert row.git_repository_branch == "master"
        assert row.git_commit_hash == "abc123def456"
        assert row.build_architecture == "arm64"
        assert row.build_compiler == "gcc-12"
        assert row.build_config_name == "defconfig"
        assert row.test_origin == "maestro"

    actual = {
        (
            row.path_group,
            row.is_boot,
            row.issue_id,
            row.issue_uncategorized,
            row.hardware_key,
            row.test_lab,
            row.test_platform,
        ): {name: getattr(row, name) for name in COUNTERS}
        for row in rows
    }
    assert actual == expected
