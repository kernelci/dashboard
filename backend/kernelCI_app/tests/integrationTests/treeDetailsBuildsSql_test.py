"""Compare SQL filtering and cached responses with the original Builds pipeline."""

import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.db import connection
from django.test import RequestFactory
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from kernelCI_app.constants.general import (
    MAESTRO_DUMMY_BUILD_PREFIX,
    UNCATEGORIZED_STRING,
    UNKNOWN_STRING,
)
from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.helpers.filters import FilterParams
from kernelCI_app.helpers.treeDetails import (
    decide_if_is_build_filtered_out,
    decide_if_is_full_row_filtered_out,
    get_build,
    get_current_row_data,
)
from kernelCI_app.models import Builds, Checkouts, Incidents, Issues, Labs
from kernelCI_app.queries.tree import get_tree_data
from kernelCI_app.queries.treeBuilds import get_tree_builds_response
from kernelCI_app.views.treeDetailsBuildsView import (
    TreeDetailsBuilds,
    TreeDetailsBuildsDirect,
)

pytestmark = pytest.mark.django_db
IDENTITY = dict(
    origin="maestro",
    git_url=None,
    git_branch="master",
    commit_hash="abc",
    tree_name="fixture",
)


def legacy_response(filters, **identity):
    # Keep the original shared query and filter helpers as an independent oracle.
    with (
        patch("kernelCI_app.queries.tree.get_query_cache", return_value=None),
        patch("kernelCI_app.queries.tree.set_query_cache"),
    ):
        rows = get_tree_data(
            data_type="builds",
            origin_param=identity["origin"],
            git_url_param=identity["git_url"],
            git_branch_param=identity["git_branch"],
            tree_name=identity["tree_name"],
            commit_hash=identity["commit_hash"],
        )
    if not rows:
        return {"error": ClientStrings.TREE_NO_RESULTS}
    if len(rows) == 1 and rows[0][14] is None:
        return {"error": ClientStrings.TREE_BUILDS_NO_RESULTS}
    builds = {}
    instance = SimpleNamespace(filters=filters)
    for row in rows:
        data = get_current_row_data(row)
        if decide_if_is_full_row_filtered_out(instance, data):
            continue
        if data["build_id"] is None or data["build_id"].startswith(
            MAESTRO_DUMMY_BUILD_PREFIX
        ):
            continue
        if not decide_if_is_build_filtered_out(instance, data):
            builds.setdefault(data["build_id"], get_build(data).model_dump())
    return {"builds": list(builds.values())}


def canonical(response):
    if "builds" in response:
        response = {"builds": sorted(response["builds"], key=lambda b: b["id"])}
    return json.dumps(response, sort_keys=True, default=str)


@pytest.fixture
def dataset():
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
    lab = Labs.objects.create(name="registered-lab")
    a = Issues.objects.create(
        id="a", version=1, origin="maestro", field_timestamp=timezone.now()
    )
    b = Issues.objects.create(
        id="b",
        version=2,
        origin="maestro",
        field_timestamp=timezone.now() - timedelta(days=1),
    )
    builds = []
    variants = [
        (
            "FAIL",
            10.9,
            "arm64",
            "gcc",
            "defconfig",
            {"platform": "board", "lab": "misc-lab"},
        ),
        (None, None, None, None, None, None),
        ("PASS", 0.0, "", "", "", {}),
        ("NULL", -1.9, "x86_64", "clang", "tiny", {"platform": None}),
        ("FAIL", 20.1, "arm64", "clang", "tiny", {"platform": "", "lab": ""}),
        ("FAIL", 10.0, "x86_64", "gcc", "defconfig", {"platform": 123}),
        ("FAIL", float("nan"), "arm64", "gcc", "defconfig", {}),
    ]
    for index, (status, duration, arch, compiler, config, misc) in enumerate(variants):
        builds.append(
            Builds.objects.create(
                id=f"build-{index}",
                checkout=checkout,
                origin="other" if index == 4 else "maestro",
                status=status,
                duration=duration,
                architecture=arch,
                compiler=compiler,
                config_name=config,
                misc=misc,
                lab=lab if index == 0 else None,
            )
        )
    for index, (build, issue, test_id) in enumerate(
        [
            (builds[0], a, None),
            (builds[0], b, None),
            (builds[0], b, "test-only"),
            (builds[1], a, "test-only"),
            (builds[4], b, None),
        ]
    ):
        Incidents.objects.create(
            id=f"incident-{index}",
            origin="maestro",
            build=build,
            issue=issue,
            issue_version=issue.version,
            test_id=test_id,
        )
    Incidents.objects.create(
        id="missing-issue",
        origin="maestro",
        build=builds[0],
        issue_id="missing",
        issue_version=1,
    )
    for build_id in ["maestro:dummy_fixture", "maestro:dummyXfixture"]:
        Builds.objects.create(
            id=build_id, checkout=checkout, origin="maestro", status="FAIL"
        )
    yield checkout
    cache.clear()


FILTER_CASES = [
    {},
    *[
        {"filterArchitecture": value}
        for value in [{"arm64"}, {UNKNOWN_STRING}, {""}, {"arm64", "x86_64"}]
    ],
    *[{"filterCompiler": value} for value in [{"gcc"}, {UNKNOWN_STRING}, {""}]],
    *[{"filterConfigs": value} for value in [{"tiny"}, {UNKNOWN_STRING}, {""}]],
    *[{"filterBuildStatus": value} for value in [{"FAIL"}, {"NULL"}, {"PASS", "FAIL"}]],
    *[
        {"filterHardware": value}
        for value in [{"board"}, {UNKNOWN_STRING}, {""}, {"123"}]
    ],
    *[{"filterBuildDurationMin": value} for value in [-1, 0, 10, 11]],
    *[{"filterBuildDurationMax": value} for value in [-1, 0, 10, 11]],
    {"filterBuildDurationMin": 10, "filterBuildDurationMax": 10},
    {"filter_build_origin": {"maestro"}},
    {"filter_build_origin": {"other"}},
    {
        "filterArchitecture": {"arm64"},
        "filterCompiler": {"gcc"},
        "filterBuildStatus": {"FAIL"},
    },
    {"filterArchitecture": {"missing"}},
]
ISSUE_CASES = [
    set(),
    {("a", 1)},
    {("b", 2)},
    {("b", 1)},
    {(UNCATEGORIZED_STRING, None)},
    {("a", 1), (UNCATEGORIZED_STRING, None)},
    {UNCATEGORIZED_STRING},
]


@pytest.mark.parametrize("attributes", FILTER_CASES)
@pytest.mark.parametrize("issues", ISSUE_CASES)
def test_sql_filters_match_legacy(dataset, attributes, issues):
    filters = FilterParams(RequestFactory().get("/"))
    for field, value in attributes.items():
        setattr(filters, field, value)
    filters.filterIssues["build"] = issues
    expected = canonical(legacy_response(filters, **IDENTITY))
    actual = get_tree_builds_response(filters=filters, **IDENTITY)
    assert canonical(actual) == expected
    assert canonical(get_tree_builds_response(filters=filters, **IDENTITY)) == expected


@pytest.mark.parametrize(
    "labs", [{"registered-lab"}, {"misc-lab"}, {UNKNOWN_STRING}, {""}]
)
def test_lab_precedence_and_fallback(dataset, labs):
    filters = FilterParams(RequestFactory().get("/"))
    filters.filter_labs["build"] = labs
    assert canonical(
        get_tree_builds_response(filters=filters, **IDENTITY)
    ) == canonical(legacy_response(filters, **IDENTITY))


def test_cache_is_final_response_and_filter_specific(
    dataset, django_assert_num_queries
):
    filters = FilterParams(RequestFactory().get("/"))
    unfiltered = get_tree_builds_response(filters=filters, **IDENTITY)
    filters.filterArchitecture = {"arm64"}
    filtered = get_tree_builds_response(filters=filters, **IDENTITY)
    assert len(filtered["builds"]) < len(unfiltered["builds"])
    # A hit must bypass SQL and model validation, not rebuild from cached tuples.
    with (
        django_assert_num_queries(0),
        patch(
            "kernelCI_app.queries.treeBuilds.BuildHistoryItem.model_validate",
            side_effect=AssertionError("cache hit validated raw data"),
        ),
    ):
        assert canonical(
            get_tree_builds_response(filters=filters, **IDENTITY)
        ) == canonical(filtered)


@pytest.mark.parametrize(
    "checkouts,add_dummy", [(0, False), (1, False), (2, False), (1, True)]
)
def test_empty_checkout_and_dummy_only_contract(
    checkouts, add_dummy, django_assert_num_queries
):
    cache.clear()
    for index in range(checkouts):
        checkout = Checkouts.objects.create(
            id=f"empty-{index}",
            origin="maestro",
            tree_name="fixture",
            git_repository_branch="master",
            git_commit_hash="abc",
            field_timestamp=timezone.now(),
        )
    if add_dummy:
        Builds.objects.create(
            id="maestro:dummy_test", origin="maestro", checkout=checkout
        )
    filters = FilterParams(RequestFactory().get("/"))
    expected = legacy_response(filters, **IDENTITY)
    assert get_tree_builds_response(filters=filters, **IDENTITY) == expected
    with django_assert_num_queries(0):
        assert get_tree_builds_response(filters=filters, **IDENTITY) == expected
    cache.clear()


@pytest.mark.parametrize("direct", [True, False])
@pytest.mark.parametrize("commit", ["abc", "v-test"])
def test_both_url_variants_and_commit_tags(dataset, direct, commit):
    request = APIRequestFactory().get(
        "/",
        {
            "origin": "maestro",
            "git_url": dataset.git_repository_url,
            "git_branch": "master",
        },
    )
    if direct:
        response = TreeDetailsBuildsDirect.as_view()(
            request,
            tree_name="fixture",
            git_branch="master",
            commit_hash=commit,
        )
    else:
        response = TreeDetailsBuilds.as_view()(request, commit_hash=commit)
    assert response.status_code == 200
    identity = dict(IDENTITY, commit_hash=commit)
    if not direct:
        identity.update(tree_name=None, git_url=dataset.git_repository_url)
    assert canonical(response.data) == canonical(
        legacy_response(FilterParams(request), **identity)
    )


def test_combined_categories_and_multiple_values(dataset):
    filters = FilterParams(RequestFactory().get("/"))
    filters.filterArchitecture = {"arm64", "x86_64"}
    filters.filterCompiler = {"gcc", "clang"}
    filters.filterConfigs = {"defconfig", "tiny"}
    filters.filterBuildStatus = {"FAIL", "NULL"}
    filters.filter_build_origin = {"maestro", "other"}
    filters.filter_labs["build"] = {"registered-lab", UNKNOWN_STRING}
    filters.filterBuildDurationMin = 10
    filters.filterBuildDurationMax = 21
    filters.filterIssues["build"] = {("a", 1), ("b", 2)}
    actual = get_tree_builds_response(filters=filters, **IDENTITY)
    assert canonical(actual) == canonical(legacy_response(filters, **IDENTITY))
    assert [b["id"] for b in actual["builds"]] == ["build-0", "build-4"]


def test_matching_issue_timestamp_preserves_order(dataset):
    filters = FilterParams(RequestFactory().get("/"))
    filters.filterIssues["build"] = {("a", 1), ("b", 2)}
    actual = get_tree_builds_response(filters=filters, **IDENTITY)
    assert actual == legacy_response(filters, **IDENTITY)
    assert [b["id"] for b in actual["builds"]] == ["build-0", "build-4"]


def test_multiple_checkouts_do_not_mix_build_metadata(dataset):
    rerun = Checkouts.objects.create(
        id="rerun",
        origin="maestro",
        tree_name="fixture",
        git_repository_branch="master",
        git_repository_url="https://another.invalid/linux.git",
        git_commit_hash="abc",
        field_timestamp=timezone.now(),
    )
    Builds.objects.create(
        id="rerun-build", origin="maestro", checkout=rerun, status="PASS"
    )
    filters = FilterParams(RequestFactory().get("/"))
    actual = get_tree_builds_response(filters=filters, **IDENTITY)
    assert canonical(actual) == canonical(legacy_response(filters, **IDENTITY))
    build = next(b for b in actual["builds"] if b["id"] == "rerun-build")
    assert build["git_repository_url"] == rerun.git_repository_url


@pytest.mark.parametrize("branch", [None, ""])
def test_null_branch_and_url_selection(branch):
    cache.clear()
    checkout = Checkouts.objects.create(
        id="null-url",
        origin="maestro",
        tree_name="fixture",
        git_repository_branch=None,
        git_repository_url=None,
        git_commit_hash="abc",
        field_timestamp=timezone.now(),
    )
    Builds.objects.create(
        id="null-build", checkout=checkout, origin="maestro", status="PASS"
    )
    filters = FilterParams(RequestFactory().get("/"))
    identity = dict(IDENTITY, git_branch=branch)
    assert get_tree_builds_response(filters=filters, **identity) == legacy_response(
        filters, **identity
    )
    cache.clear()


def test_commit_tag_uses_latest_hash_before_tree_selection(dataset):
    Checkouts.objects.create(
        id="other-tree",
        origin="maestro",
        tree_name="other",
        git_repository_branch="master",
        git_commit_hash="new-hash",
        git_commit_tags=["v-test"],
        field_timestamp=timezone.now() + timedelta(days=1),
    )
    filters = FilterParams(RequestFactory().get("/"))
    identity = dict(IDENTITY, commit_hash="v-test")
    assert get_tree_builds_response(filters=filters, **identity) == legacy_response(
        filters, **identity
    )
    assert get_tree_builds_response(filters=filters, **identity) == {
        "error": ClientStrings.TREE_NO_RESULTS
    }


def test_filtering_and_deduplication_happen_before_transfer(dataset):
    filters = FilterParams(RequestFactory().get("/"))
    filters.filterArchitecture = {"arm64"}
    filters.filterBuildStatus = {"FAIL"}
    filters.filterBuildDurationMin = 10
    filters.filterIssues["build"] = {("a", 1)}
    transferred_rows = []

    def record(execute, sql, params, many, context):
        result = execute(sql, params, many, context)
        transferred_rows.append(context["cursor"].rowcount)
        return result

    with connection.execute_wrapper(record):
        response = get_tree_builds_response(filters=filters, **IDENTITY)
    assert transferred_rows == [1]
    assert [b["id"] for b in response["builds"]] == ["build-0"]
