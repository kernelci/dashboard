"""Integration tests for the recompute_lab_daily management command."""

from datetime import date, datetime, timezone

import pytest
from django.core.management import call_command

from kernelCI_app.models import LabDaily, Labs
from kernelCI_app.tests.factories import BuildFactory, CheckoutFactory, TestFactory

DAY = date(2026, 10, 14)
IN_DAY = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
LAST_SECOND = datetime(2026, 10, 14, 23, 59, 59, tzinfo=timezone.utc)
NEXT_DAY = datetime(2026, 10, 15, tzinfo=timezone.utc)


@pytest.mark.django_db
def test_counts_one_day_per_lab():
    lab = Labs.objects.create(name="lab-a")
    tests_only_lab = Labs.objects.create(name="lab-b")
    checkout = CheckoutFactory(origin="maestro")

    def build(status, start_time=IN_DAY, lab=lab, **kwargs):
        return BuildFactory(
            checkout=checkout,
            lab=lab,
            start_time=start_time,
            status=status,
            **kwargs,
        )

    parent = build("PASS")
    build("PASS", start_time=LAST_SECOND)
    build("FAIL")
    build("ERROR")
    build("PASS", lab=None)
    build("PASS", id="maestro:dummy_build")
    build("PASS", start_time=NEXT_DAY)

    def test(path, status, start_time=IN_DAY, lab=lab):
        return TestFactory(
            build=parent, lab=lab, path=path, start_time=start_time, status=status
        )

    test("boot", "PASS")
    test("boot.nfs", "FAIL")
    test("boot", None)
    test("baseline.login", "PASS")
    test("bootrr.deferred-probe-empty", "PASS")
    test("baseline.login", "FAIL")
    test("baseline.login", "SKIP")
    test(None, "PASS")
    test("baseline.login", "PASS", lab=None)
    test("baseline.login", "PASS", start_time=NEXT_DAY)
    test("baseline.login", "PASS", lab=tests_only_lab)

    call_command("recompute_lab_daily", day=DAY)
    call_command("recompute_lab_daily", day=DAY)

    rows = {
        row.pop("lab__name"): row
        for row in LabDaily.objects.filter(day=DAY).values(
            "lab__name",
            "origin",
            "build_pass",
            "build_failed",
            "build_inc",
            "boot_pass",
            "boot_failed",
            "boot_inc",
            "test_pass",
            "test_failed",
            "test_inc",
        )
    }
    assert rows == {
        "lab-a": {
            "origin": "maestro",
            "build_pass": 2,
            "build_failed": 1,
            "build_inc": 1,
            "boot_pass": 1,
            "boot_failed": 1,
            "boot_inc": 1,
            "test_pass": 2,
            "test_failed": 1,
            "test_inc": 1,
        },
        "lab-b": {
            "origin": "maestro",
            "build_pass": 0,
            "build_failed": 0,
            "build_inc": 0,
            "boot_pass": 0,
            "boot_failed": 0,
            "boot_inc": 0,
            "test_pass": 1,
            "test_failed": 0,
            "test_inc": 0,
        },
    }
