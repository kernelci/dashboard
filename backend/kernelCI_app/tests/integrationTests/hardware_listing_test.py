"""Integration tests for hardware listing queries over daily aggregates."""

from datetime import timedelta

import pytest

from kernelCI_app.models import HardwareDailyBuilds, HardwareDailyTests, LatestCheckout
from kernelCI_app.queries.hardware import (
    get_hardware_filters,
    get_hardware_listing_data,
    get_hardware_listing_data_by_revision,
)
from kernelCI_app.tests.factories import BuildFactory
from kernelCI_app.tests.integrationTests.recompute_hardware_daily_test import (
    DAY_START,
    _checkout,
    _recompute,
    _test_on,
)

WINDOW = (DAY_START - timedelta(hours=1), DAY_START + timedelta(hours=1))


def _independent_filter_fixture():
    checkout = _checkout(
        origin="checkout-origin",
        tree_name="tree",
        git_repository_url="https://example.com/linux.git",
        git_repository_branch="main",
        git_commit_hash="a" * 40,
    )
    selected_build = BuildFactory(
        checkout=checkout,
        origin="selected-build-origin",
        misc={"lab": "selected-build-lab"},
        status="PASS",
    )
    other_build = BuildFactory(
        checkout=checkout,
        origin="other-build-origin",
        misc={"lab": "other-build-lab"},
        status="FAIL",
    )
    _test_on(
        selected_build,
        "pA",
        origin="other-test-origin",
        lab="other-test-lab",
        status="FAIL",
    )
    _test_on(
        other_build,
        "pA",
        origin="selected-test-origin",
        lab="selected-test-lab",
        status="PASS",
    )
    _recompute()
    return checkout


@pytest.mark.django_db
def test_listing_filters_builds_and_tests_independently():
    _independent_filter_fixture()
    start, end = WINDOW

    rows = get_hardware_listing_data(
        start_date=start,
        end_date=end,
        checkout_origin=["checkout-origin"],
        build_origin=["selected-build-origin"],
        test_origin=["selected-test-origin"],
        build_lab=["selected-build-lab"],
        test_lab=["selected-test-lab"],
        commits_list=["a" * 40],
    )

    assert len(rows) == 1
    assert rows[0][0] == "pA"
    assert rows[0][2:5] == (1, 0, 0)
    assert rows[0][8:11] == (1, 0, 0)


@pytest.mark.django_db
def test_filters_api_lists_every_option_in_the_window():
    _independent_filter_fixture()
    start, end = WINDOW

    assert get_hardware_filters(start_date=start, end_date=end) == {
        "checkout_origins": ["checkout-origin"],
        "build_origins": ["other-build-origin", "selected-build-origin"],
        "test_origins": ["other-test-origin", "selected-test-origin"],
        "build_labs": ["other-build-lab", "selected-build-lab"],
        "test_labs": ["other-test-lab", "selected-test-lab"],
    }


@pytest.mark.django_db
def test_by_revision_listing_honours_side_filters():
    _independent_filter_fixture()

    revision_rows = get_hardware_listing_data_by_revision(
        checkout_origin=["checkout-origin"],
        build_origin=["selected-build-origin"],
        test_origin=["selected-test-origin"],
        build_lab=["selected-build-lab"],
        test_lab=["selected-test-lab"],
        tree_name="tree",
        git_repository_url="https://example.com/linux.git",
        git_repository_branch="main",
        git_commit_hash="a" * 40,
    )
    assert revision_rows[0][2] == 1
    assert revision_rows[0][8] == 1


@pytest.mark.django_db
def test_a_narrowed_side_decides_which_platforms_are_listed():
    checkout = _checkout(origin="maestro")
    build = BuildFactory(checkout=checkout, origin="maestro", status="PASS")
    _test_on(build, "tested-here", lab="lava-broonie")
    _test_on(build, "tested-elsewhere", lab="lava-collabora")
    _recompute()
    LatestCheckout.objects.create(
        checkout_id=checkout.id, start_time=DAY_START, origin="maestro"
    )

    def platforms(**filters):
        rows = get_hardware_listing_data(
            start_date=WINDOW[0],
            end_date=WINDOW[1],
            **{
                "checkout_origin": None,
                "build_origin": None,
                "test_origin": None,
                "build_lab": None,
                "test_lab": None,
                **filters,
            },
        )
        return [row[0] for row in rows]

    assert platforms() == ["tested-elsewhere", "tested-here"]
    assert platforms(test_lab=["lava-broonie"]) == ["tested-here"]
    assert platforms(build_origin=["maestro"], test_lab=["lava-broonie"]) == [
        "tested-here"
    ]
    assert platforms(test_origin=["nobody"]) == []


@pytest.mark.django_db
def test_unknown_checkout_origin_is_listed_until_an_origin_is_chosen():
    checkout = _checkout(origin="maestro")
    _test_on(BuildFactory(checkout=checkout, status="PASS"), "pA")
    _recompute()
    HardwareDailyBuilds.objects.update(checkout_origin=None)
    HardwareDailyTests.objects.update(checkout_origin=None)
    LatestCheckout.objects.create(
        checkout_id=checkout.id, start_time=DAY_START, origin="maestro"
    )

    def listing(checkout_origin):
        return get_hardware_listing_data(
            start_date=WINDOW[0],
            end_date=WINDOW[1],
            checkout_origin=checkout_origin,
            build_origin=None,
            test_origin=None,
            build_lab=None,
            test_lab=None,
        )

    assert [row[0] for row in listing(None)] == ["pA"]
    assert listing(["maestro"]) == []
