"""Integration tests for the recompute_hardware_daily management command."""

from datetime import date, datetime, timedelta, timezone

import pytest
from django.core.management import call_command
from django.db import connections

from kernelCI_app.constants.general import MAESTRO_DUMMY_BUILD_PREFIX
from kernelCI_app.management.commands.recompute_hardware_daily import lock_key
from kernelCI_app.models import HardwareDailyBuilds, HardwareDailyTests, Tests
from kernelCI_app.tests.factories import BuildFactory, CheckoutFactory, TestFactory

DAY = date(2026, 7, 15)
DAY_START = datetime(2026, 7, 15, 10, tzinfo=timezone.utc)


def _checkout(**kwargs):
    return CheckoutFactory(start_time=DAY_START, **kwargs)


def _test_on(
    build,
    platform,
    *,
    path="ltp.x",
    status="PASS",
    lab="lab-1",
    compatibles=None,
    **kwargs,
):
    TestFactory(
        build=build,
        path=path,
        status=status,
        environment_misc={"platform": platform},
        environment_compatible=compatibles,
        misc={"runtime": lab} if lab else {},
        **kwargs,
    )


def _recompute():
    call_command("recompute_hardware_daily", day=DAY)


@pytest.mark.django_db
def test_boot_and_test_counters_are_split():
    """Boot paths, plain tests and anything but PASS/FAIL land in their own counter."""
    build = BuildFactory(checkout=_checkout(), status="PASS")
    _test_on(build, "pA", path="boot", status="PASS")
    _test_on(build, "pA", path="boot.nfs", status="FAIL")
    _test_on(build, "pA", path="boot", status=None)
    _test_on(build, "pA", path="ltp.x", status="SKIP")
    _test_on(build, "pA", path=None, status="PASS")
    other_day = CheckoutFactory(start_time=DAY_START - timedelta(days=1))
    _test_on(BuildFactory(checkout=other_day, status="PASS"), "pA", path="boot")

    _recompute()

    row = HardwareDailyTests.objects.get()
    assert row.checkout_day == DAY
    assert (row.boot_pass, row.boot_failed, row.boot_inc) == (1, 1, 1)
    assert (row.test_pass, row.test_failed, row.test_inc) == (1, 0, 1)


@pytest.mark.django_db
def test_dummy_build_is_not_counted_but_its_tests_are():
    checkout = _checkout()
    real = BuildFactory(checkout=checkout, status="PASS")
    dummy = BuildFactory(
        checkout=checkout, id=f"{MAESTRO_DUMMY_BUILD_PREFIX}1", status="PASS"
    )
    _test_on(real, "pA", path="boot")
    _test_on(dummy, "pA", path="boot")

    _recompute()

    assert HardwareDailyBuilds.objects.get().build_pass == 1
    assert HardwareDailyTests.objects.get().boot_pass == 2


@pytest.mark.django_db
def test_build_is_counted_once_per_platform():
    build = BuildFactory(checkout=_checkout(), status="PASS")
    _test_on(build, "pA")
    _test_on(build, "pA")
    _test_on(build, "pB")

    _recompute()

    counted = HardwareDailyBuilds.objects.order_by("platform")
    assert [(row.platform, row.build_pass) for row in counted] == [("pA", 1), ("pB", 1)]


@pytest.mark.django_db
def test_lab_comes_from_misc_and_falls_back_to_origin():
    checkout = _checkout(origin="maestro")
    from_misc = BuildFactory(
        checkout=checkout, status="PASS", misc={"lab": "build-lab"}, origin="maestro"
    )
    from_runtime = BuildFactory(
        checkout=checkout, status="PASS", misc={"runtime": "run-lab"}, origin="maestro"
    )
    _test_on(from_misc, "pA", lab=None)
    _test_on(from_runtime, "pB", lab="test-lab")

    _recompute()

    assert HardwareDailyTests.objects.get(platform="pA").test_lab == "maestro"
    assert HardwareDailyTests.objects.get(platform="pB").test_lab == "test-lab"
    assert HardwareDailyBuilds.objects.get(platform="pA").build_lab == "build-lab"
    assert HardwareDailyBuilds.objects.get(platform="pB").build_lab == "run-lab"


@pytest.mark.django_db
def test_checkout_origin_is_stored_on_both_tables():
    checkout = _checkout(origin="maestro")
    build = BuildFactory(checkout=checkout, status="PASS", origin="maestro")
    _test_on(build, "pA", path="boot", origin="linaro")

    _recompute()

    assert HardwareDailyBuilds.objects.get().checkout_origin == "maestro"
    test_row = HardwareDailyTests.objects.get()
    assert test_row.checkout_origin == "maestro"
    assert test_row.test_origin == "linaro"


@pytest.mark.django_db
def test_rerun_replaces_the_day_without_duplicating():
    _test_on(BuildFactory(checkout=_checkout(), status="PASS"), "pA", path="boot")

    _recompute()
    _recompute()

    assert HardwareDailyTests.objects.get().boot_pass == 1
    assert HardwareDailyBuilds.objects.get().build_pass == 1


@pytest.mark.django_db
def test_compatibles_resolve_to_the_most_specific_chain():
    """Labs disagreeing on a platform get one label, the longest chain reported."""
    build = BuildFactory(checkout=_checkout(), status="PASS")
    _test_on(build, "pA", lab="lab-1", compatibles=["rockchip", "rk3399"])
    _test_on(build, "pA", lab="lab-2", compatibles=["rk3399"])
    _test_on(build, "pA", lab="lab-3", compatibles=None)

    _recompute()

    assert HardwareDailyBuilds.objects.get().compatibles == ["rockchip", "rk3399"]
    labelled = HardwareDailyTests.objects.values_list("compatibles", flat=True)
    assert list(labelled) == [["rockchip", "rk3399"]] * 3


@pytest.mark.django_db
def test_day_locked_by_another_run_is_skipped():
    _test_on(BuildFactory(checkout=_checkout(), status="PASS"), "pA", path="boot")

    other_run = connections.create_connection("default")
    with other_run.cursor() as cursor:
        cursor.execute(
            "SELECT pg_advisory_lock(%s, %s)",
            [lock_key("hardware_daily_builds"), DAY.toordinal()],
        )
        _recompute()
    other_run.close()

    assert not HardwareDailyTests.objects.exists()


@pytest.mark.django_db
def test_pruned_raw_data_keeps_the_existing_rows():
    _test_on(BuildFactory(checkout=_checkout(), status="PASS"), "pA", path="boot")
    _recompute()

    Tests.objects.all().delete()
    _recompute()

    assert HardwareDailyTests.objects.get().boot_pass == 1
    assert HardwareDailyBuilds.objects.get().build_pass == 1
