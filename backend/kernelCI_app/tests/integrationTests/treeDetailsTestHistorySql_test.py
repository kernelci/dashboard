"""Compare filtered test-history SQL with the original query and filter helpers."""

import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.db import connection
from django.test import RequestFactory
from django.utils import timezone
from pydantic import ValidationError
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.general import UNCATEGORIZED_STRING, UNKNOWN_STRING
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.treeDetails import (
    decide_if_is_boot_filtered_out,
    decide_if_is_full_row_filtered_out,
    get_current_row_data,
)
from kernelCI_app.models import Builds, Checkouts, Incidents, Issues, Labs
from kernelCI_app.models import Tests as Results
from kernelCI_app.queries.tree import get_tree_data
from kernelCI_app.queries.treeTestHistory import get_tree_test_history_response
from kernelCI_app.typeModels.commonDetails import TestHistoryItem as HistoryItem
from kernelCI_app.utils import is_boot
from kernelCI_app.views.treeDetailsBootsView import (
    TreeDetailsBoots,
    TreeDetailsBootsDirect,
)

pytestmark = pytest.mark.django_db
IDENTITY = dict(
    origin="maestro",
    git_url=None,
    git_branch="master",
    commit_hash="abc",
    tree_name="fixture",
)


@pytest.fixture
def data_type():
    return "boots"


def legacy_response(filters, data_type, full_environment_misc=False, **identity):
    with (
        patch("kernelCI_app.queries.tree.get_query_cache", return_value=None),
        patch("kernelCI_app.queries.tree.set_query_cache"),
    ):
        rows = get_tree_data(
            data_type=data_type,
            origin_param=identity["origin"],
            git_url_param=identity["git_url"],
            git_branch_param=identity["git_branch"],
            commit_hash=identity["commit_hash"],
            tree_name=identity["tree_name"],
        )
    if not rows:
        return {"error": ClientStrings.TREE_NO_RESULTS}
    items = {}
    instance = SimpleNamespace(filters=filters)
    for row in rows:
        data = get_current_row_data(row, full_environment_misc=full_environment_misc)
        if (
            decide_if_is_full_row_filtered_out(instance, data)
            or data["test_id"] is None
        ):
            continue
        if not is_boot(data["test_path"]):
            continue
        if decide_if_is_boot_filtered_out(instance, data):
            continue
        items.setdefault(
            data["test_id"], HistoryItem(**data["history_item"]).model_dump()
        )
    return {data_type: list(items.values())}


def canonical(response):
    if "error" not in response:
        response = {
            k: sorted(v, key=lambda item: item["id"]) for k, v in response.items()
        }
    return json.dumps(response, sort_keys=True, default=str)


@pytest.fixture
def dataset(data_type):
    cache.clear()
    checkout = Checkouts.objects.create(
        id="checkout",
        origin="maestro",
        tree_name="fixture",
        git_repository_branch="master",
        git_repository_url="https://fixture.invalid/linux.git",
        git_commit_hash="abc",
        git_commit_tags=["v-test"],
        field_timestamp=timezone.now(),
    )
    build = Builds.objects.create(
        id="build",
        origin="maestro",
        checkout=checkout,
        status="PASS",
        architecture="arm64",
        compiler="gcc",
        config_name="defconfig",
        misc={"platform": "build-board", "unused": "x" * 1024},
    )
    failed = Builds.objects.create(
        id="failed-build", origin="maestro", checkout=checkout, status="FAIL"
    )
    dummy = Builds.objects.create(
        id="maestro:dummy_test",
        origin="maestro",
        checkout=checkout,
        status="PASS",
        architecture="x86_64",
        compiler="clang",
        config_name="tiny",
        misc={"platform": "dummy-board"},
    )
    lab = Labs.objects.create(name="registered-lab")
    variants = [
        (
            build,
            "FAIL",
            10.9,
            ["board", "second-board"],
            {"platform": "env-board", "extra": "retained"},
        ),
        (build, "PASS", 0.0, None, None),
        (
            failed,
            None,
            None,
            [UNKNOWN_STRING],
            {"platform": "env-board", "extra": "retained"},
        ),
        (build, "FAIL", -1.9, None, {"extra": "retained"}),
        (build, "PASS", 20.1, None, None),
        (build, "PASS", 10.0, [UNKNOWN_STRING], {"platform": ""}),
        (failed, "NULL", float("nan"), None, {}),
        (build, "FAIL", 30.0, None, {"platform": "123"}),
        (dummy, "FAIL", 10.0, None, None),
        (build, "", 0, [UNKNOWN_STRING], {"platform": UNKNOWN_STRING}),
        (failed, "PASS", 10.0, None, None),
    ]
    results = []
    for index, (parent, status, duration, compatible, environment) in enumerate(
        variants
    ):
        path = "boot" if index == 0 else f"boot.{index}"
        if index == 2:
            path = "boot.%_special"
        results.append(
            Results.objects.create(
                id=f"result-{index}",
                build=parent,
                origin="other" if index == 4 else "maestro",
                path=path,
                status=status,
                duration=duration,
                environment_compatible=compatible,
                environment_misc=environment,
                lab=lab if index == 0 else None,
                misc={
                    "runtime": "runtime-lab" if index != 5 else "",
                    "unused": "y" * 1024,
                },
            )
        )
    for test_id, path, build_id in [
        ("other-category", "suite.other", build.id),
        ("null-path", None, build.id),
        ("orphan", "boot.orphan", "missing-build"),
    ]:
        Results.objects.create(
            id=test_id, origin="maestro", path=path, build_id=build_id, status="FAIL"
        )
    a = Issues.objects.create(
        id="a", version=1, origin="maestro", field_timestamp=timezone.now()
    )
    b = Issues.objects.create(
        id="b",
        version=2,
        origin="maestro",
        field_timestamp=timezone.now() - timedelta(days=1),
    )
    for index, (result, issue) in enumerate(
        [(results[0], a), (results[0], b), (results[1], b), (results[8], a)]
    ):
        Incidents.objects.create(
            id=f"incident-{index}",
            origin="maestro",
            build=build,
            test=result,
            issue=issue,
            issue_version=issue.version,
        )
    for result, version in [(results[0], 99), (results[3], 99)]:
        Incidents.objects.create(
            id="missing-version-" + result.id,
            origin="maestro",
            build=build,
            test=result,
            issue=a,
            issue_version=version,
        )
    Incidents.objects.create(
        id="build-only", origin="maestro", build=build, issue=a, issue_version=1
    )
    yield checkout
    cache.clear()


FILTER_CASES = [
    {},
    *[
        {"filterArchitecture": v}
        for v in [{"arm64"}, {UNKNOWN_STRING}, {"arm64", "x86_64"}]
    ],
    *[{"filterCompiler": v} for v in [{"gcc"}, {UNKNOWN_STRING}]],
    *[{"filterConfigs": v} for v in [{"tiny"}, {UNKNOWN_STRING}]],
    *[
        {"filterHardware": v}
        for v in [
            {"board"},
            {"second-board"},
            {"env-board"},
            {"build-board"},
            {"dummy-board"},
            {UNKNOWN_STRING},
            {""},
            {"123"},
        ]
    ],
    *[
        {"filterBootStatus": v}
        for v in [{"FAIL"}, {"PASS"}, {"NULL"}, {""}, {"FAIL", "PASS"}]
    ],
    *[{"filterBootPath": v} for v in ["boot", "%_", "BOOT", "missing"]],
    *[{"filterBootDurationMin": v} for v in [-1, 0, 10, 11]],
    *[{"filterBootDurationMax": v} for v in [-1, 0, 10, 11]],
    {"filterBootDurationMin": 10, "filterBootDurationMax": 10},
    {"filter_boot_origin": {"maestro"}},
    {"filter_boot_origin": {"other"}},
    {
        "filterArchitecture": {"arm64"},
        "filterConfigs": {"defconfig"},
        "filterBootStatus": {"FAIL"},
    },
    {
        "filterBuildStatus": {"missing"},
        "filterBuildDurationMin": 100000,
        "filter_build_origin": {"missing"},
    },
]
ISSUE_CASES = [
    set(),
    {("a", 1)},
    {("b", 2)},
    {("a", 99)},
    {(UNCATEGORIZED_STRING, None)},
    {("a", 1), ("b", 2)},
    {UNCATEGORIZED_STRING},
]


@pytest.mark.parametrize("attributes", FILTER_CASES)
@pytest.mark.parametrize("issues", ISSUE_CASES)
@pytest.mark.parametrize("full", [False, True])
def test_filters_match_legacy(dataset, data_type, attributes, issues, full):
    filters = FilterParams(RequestFactory().get("/"))
    for field, value in attributes.items():
        setattr(filters, field, value)
    filters.filterIssues["boot"] = issues
    expected = legacy_response(
        filters, data_type, full_environment_misc=full, **IDENTITY
    )
    actual = get_tree_test_history_response(
        data_type=data_type, filters=filters, full_environment_misc=full, **IDENTITY
    )
    assert canonical(actual) == canonical(expected)


@pytest.mark.parametrize(
    "field,values",
    [
        ("filter_labs", {"registered-lab"}),
        ("filter_labs", {"runtime-lab"}),
        ("filter_labs", {UNKNOWN_STRING}),
        ("filterPlatforms", {"env-board"}),
        ("filterPlatforms", {UNKNOWN_STRING}),
    ],
)
def test_lab_and_platform_filter_behavior(dataset, data_type, field, values):
    filters = FilterParams(RequestFactory().get("/"))
    getattr(filters, field)["boot"] = values
    assert canonical(
        get_tree_test_history_response(data_type=data_type, filters=filters, **IDENTITY)
    ) == canonical(legacy_response(filters, data_type, **IDENTITY))


def test_cache_contains_final_response_and_separates_full_misc(
    dataset, data_type, django_assert_num_queries
):
    filters = FilterParams(RequestFactory().get("/"))
    small = get_tree_test_history_response(
        data_type=data_type, filters=filters, **IDENTITY
    )
    full = get_tree_test_history_response(
        data_type=data_type, filters=filters, full_environment_misc=True, **IDENTITY
    )
    assert all(
        set(item["environment_misc"]) == {"platform"} for item in small[data_type]
    )
    assert any("extra" in item["environment_misc"] for item in full[data_type])
    with (
        django_assert_num_queries(0),
        patch(
            "kernelCI_app.queries.treeTestHistory.TestHistoryItem.model_validate",
            side_effect=AssertionError("cache hit revalidated rows"),
        ),
    ):
        assert canonical(
            get_tree_test_history_response(
                data_type=data_type, filters=filters, **IDENTITY
            )
        ) == canonical(small)
        assert canonical(
            get_tree_test_history_response(
                data_type=data_type,
                filters=filters,
                full_environment_misc=True,
                **IDENTITY,
            )
        ) == canonical(full)


@pytest.mark.parametrize(
    "checkouts,with_build", [(0, False), (1, False), (2, False), (1, True)]
)
def test_missing_checkout_and_empty_history(
    data_type, checkouts, with_build, django_assert_num_queries
):
    cache.clear()
    for i in range(checkouts):
        checkout = Checkouts.objects.create(
            id=f"empty-{i}",
            origin="maestro",
            tree_name="fixture",
            git_repository_branch="master",
            git_commit_hash="abc",
            field_timestamp=timezone.now(),
        )
    if with_build:
        Builds.objects.create(id="no-tests", checkout=checkout, origin="maestro")
    filters = FilterParams(RequestFactory().get("/"))
    expected = legacy_response(filters, data_type, **IDENTITY)
    assert (
        get_tree_test_history_response(data_type=data_type, filters=filters, **IDENTITY)
        == expected
    )
    with django_assert_num_queries(0):
        assert (
            get_tree_test_history_response(
                data_type=data_type, filters=filters, **IDENTITY
            )
            == expected
        )
    cache.clear()


@pytest.mark.parametrize("direct", [True, False])
@pytest.mark.parametrize("commit", ["abc", "v-test"])
def test_both_routes_and_commit_tags(dataset, data_type, direct, commit):
    request = APIRequestFactory().get(
        "/",
        {
            "origin": "maestro",
            "git_url": dataset.git_repository_url,
            "git_branch": "master",
            "full_environment_misc": "true",
        },
    )
    if direct:
        response = TreeDetailsBootsDirect.as_view()(
            request, tree_name="fixture", git_branch="master", commit_hash=commit
        )
    else:
        response = TreeDetailsBoots.as_view()(request, commit_hash=commit)
    assert response.status_code == 200
    identity = dict(IDENTITY, commit_hash=commit)
    if not direct:
        identity.update(tree_name=None, git_url=dataset.git_repository_url)
    assert canonical(response.data) == canonical(
        legacy_response(
            FilterParams(request), data_type, full_environment_misc=True, **identity
        )
    )


def test_sql_transfers_only_matching_test_once(dataset, data_type):
    filters = FilterParams(RequestFactory().get("/"))
    filters.filterHardware = {"board"}
    filters.filterIssues["boot"] = {("a", 1)}
    rows = []

    def record(execute, sql, params, many, context):
        result = execute(sql, params, many, context)
        rows.append(context["cursor"].rowcount)
        return result

    with connection.execute_wrapper(record):
        response = get_tree_test_history_response(
            data_type=data_type, filters=filters, **IDENTITY
        )
    assert rows == [1]
    assert [item["id"] for item in response[data_type]] == ["result-0"]


@pytest.mark.parametrize("platform", [None, 123])
def test_invalid_platform_validation_and_hardware_filtering(
    dataset, data_type, platform
):
    Results.objects.filter(id="result-4").update(
        environment_misc={"platform": platform}
    )
    filters = FilterParams(RequestFactory().get("/"))
    with pytest.raises(ValidationError):
        legacy_response(filters, data_type, **IDENTITY)
    with pytest.raises(ValidationError):
        get_tree_test_history_response(data_type=data_type, filters=filters, **IDENTITY)
    filters.filterHardware = {UNKNOWN_STRING}
    assert canonical(
        get_tree_test_history_response(data_type=data_type, filters=filters, **IDENTITY)
    ) == canonical(legacy_response(filters, data_type, **IDENTITY))
