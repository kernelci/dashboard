"""Integration tests for the recompute_tree_listing management command."""

import pytest
from django.core.management import call_command

from kernelCI_app.management.commands.helpers.aggregation_helpers import (
    update_tree_listing,
)
from kernelCI_app.models import TreeListing
from kernelCI_app.tests.factories import BuildFactory, CheckoutFactory, TestFactory

TREE = {
    "origin": "maestro",
    "tree_name": "mainline",
    "git_repository_url": "https://git.kernel.org/torvalds/linux.git",
    "git_repository_branch": "master",
}


@pytest.mark.django_db
def test_counts_every_checkout_of_the_tree_commit():
    checkout = CheckoutFactory(id="listing_checkout", git_commit_hash="abc", **TREE)
    same_commit = CheckoutFactory(id="listing_rerun", git_commit_hash="abc", **TREE)
    other_commit = CheckoutFactory(id="listing_other", git_commit_hash="def", **TREE)
    update_tree_listing([checkout, other_commit])

    parent = BuildFactory(checkout=checkout, status="PASS")
    BuildFactory(checkout=checkout, status="FAIL")
    BuildFactory(checkout=checkout, status=None)
    BuildFactory(checkout=same_commit, status="PASS")
    dummy = BuildFactory(checkout=checkout, id="maestro:dummy_build", status="PASS")
    other = BuildFactory(checkout=other_commit, status="PASS")

    def test(path, status, build=parent):
        return TestFactory(build=build, path=path, status=status)

    test("boot", "PASS")
    test("boot.nfs", "FAIL")
    test("boot", None)
    test("bootrr.deferred-probe-empty", "PASS")
    test(None, "PASS")
    test("baseline.login", "FAIL")
    test("baseline.login", "SKIP")
    test("baseline.login", "PASS", build=dummy)
    test("baseline.login", "PASS", build=other)

    call_command("recompute_tree_listing", checkout_id=checkout.id)
    call_command("recompute_tree_listing", checkout_id=checkout.id)

    assert TreeListing.objects.filter(git_commit_hash="abc").values(
        "build_pass",
        "build_failed",
        "build_inc",
        "boot_pass",
        "boot_failed",
        "boot_inc",
        "test_pass",
        "test_failed",
        "test_inc",
    ).get() == {
        "build_pass": 2,
        "build_failed": 1,
        "build_inc": 1,
        "boot_pass": 1,
        "boot_failed": 1,
        "boot_inc": 1,
        "test_pass": 3,
        "test_failed": 1,
        "test_inc": 1,
    }
    assert TreeListing.objects.get(git_commit_hash="def").build_pass == 0
