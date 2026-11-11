import re
from pathlib import Path

import pytest
from prometheus_client import REGISTRY
from rest_framework.test import APIRequestFactory

from kernelCI_app.views import visibleTimeView
from kernelCI_app.views.visibleTimeView import (
    DASHBOARD_ROUTES,
    VisibleTimeView,
    route_label,
)

ROUTE = "/tree/mainline/master"
REPO_ROOT = Path(__file__).resolve().parents[5]


@pytest.fixture(autouse=True)
def route_label_cache(monkeypatch):
    visibleTimeView._tree_cache = {("mainline", "master"), ("mainline", "build")}
    visibleTimeView._hardware_cache = {"bcm2711-rpi-4-b", "board-a", "board-b"}
    monkeypatch.setattr(visibleTimeView, "_tree_pair_in_checkouts", lambda _pair: False)
    monkeypatch.setattr(
        visibleTimeView, "_hardware_id_in_status", lambda _hardware_id: False
    )


def _sample(name: str, route: str) -> float:
    return REGISTRY.get_sample_value(name, {"route": route}) or 0


def _post(payload: dict):
    request = APIRequestFactory().post(
        "/api/analytics/visible/",
        data=payload,
        format="json",
    )
    return VisibleTimeView.as_view()(request)


def test_valid_beacon_observes_visible_seconds():
    before_sum = _sample("dashboard_route_visible_seconds_sum", ROUTE)
    before_count = _sample("dashboard_route_visible_seconds_count", ROUTE)

    response = _post({"route": ROUTE, "time_ms": 20_000})

    assert response.status_code == 204
    assert _sample("dashboard_route_visible_seconds_sum", ROUTE) == before_sum + 20
    assert _sample("dashboard_route_visible_seconds_count", ROUTE) == before_count + 1


@pytest.mark.parametrize(
    "fields",
    [
        {"route": "/not-a-route", "time_ms": 20_000},
        {"route": ROUTE, "time_ms": -1},
        {"route": ROUTE, "time_ms": "nope"},
        {"time_ms": 20_000},
        {"route": ROUTE},
    ],
)
def test_invalid_beacon_records_nothing(fields):
    before = _sample("dashboard_route_visible_seconds_count", ROUTE)
    response = _post(fields)
    assert response.status_code == 400
    assert _sample("dashboard_route_visible_seconds_count", ROUTE) == before
    assert _sample("dashboard_route_visible_seconds_count", "/not-a-route") == 0


@pytest.mark.parametrize(
    ("path", "label"),
    [
        ("/tree/mainline/master/abc", "/tree/mainline/master/$hash"),
        ("/tree/mainline/master/compare", "/tree/mainline/master/compare"),
        ("/tree/mainline/build/compare", "/tree/mainline/build/compare"),
        (
            "/hardware/bcm2711-rpi-4-b/test/maestro:1",
            "/hardware/bcm2711-rpi-4-b/test/$testId",
        ),
        ("/tree/abc/build/def", "/tree/$treeId/build/$buildId"),
    ],
)
def test_route_label(path, label):
    assert route_label(path) == label


def test_long_stay_is_capped_at_one_day():
    before_sum = _sample("dashboard_route_visible_seconds_sum", ROUTE)
    before_count = _sample("dashboard_route_visible_seconds_count", ROUTE)

    response = _post({"route": ROUTE, "time_ms": 86_400_000 + 3_600_000})

    assert response.status_code == 204
    assert _sample("dashboard_route_visible_seconds_sum", ROUTE) == before_sum + 86_400
    assert _sample("dashboard_route_visible_seconds_count", ROUTE) == before_count + 1


def test_unknown_tree_and_hardware_use_the_pattern():
    tree_label = "/tree/$treeName/$branch"
    hardware_label = "/hardware/$hardwareId"
    before_tree = _sample("dashboard_route_visible_seconds_count", tree_label)
    before_hardware = _sample("dashboard_route_visible_seconds_count", hardware_label)

    tree = _post({"route": "/tree/nope/nope", "time_ms": 1_000})
    hardware = _post({"route": "/hardware/nope", "time_ms": 1_000})

    assert tree.status_code == 204
    assert hardware.status_code == 204
    assert (
        _sample("dashboard_route_visible_seconds_count", tree_label) == before_tree + 1
    )
    assert (
        _sample("dashboard_route_visible_seconds_count", hardware_label)
        == before_hardware + 1
    )
    assert _sample("dashboard_route_visible_seconds_count", "/tree/nope/nope") == 0
    assert _sample("dashboard_route_visible_seconds_count", "/hardware/nope") == 0


def test_a_tree_found_on_miss_joins_the_cache(monkeypatch):
    calls = {"n": 0}

    def in_checkouts(pair):
        calls["n"] += 1
        return pair == ("fresh", "topic")

    monkeypatch.setattr(visibleTimeView, "_tree_pair_in_checkouts", in_checkouts)
    label = "/tree/fresh/topic"
    before = _sample("dashboard_route_visible_seconds_count", label)

    first = _post({"route": label, "time_ms": 1_000})
    second = _post({"route": label, "time_ms": 1_000})

    assert first.status_code == 204
    assert second.status_code == 204
    assert calls["n"] == 1
    assert _sample("dashboard_route_visible_seconds_count", label) == before + 2


def test_dashboard_routes_match_generated_route_tree():
    text = (REPO_ROOT / "dashboard/src/routeTree.gen.ts").read_text()
    block = re.search(r"export interface FileRoutesByTo \{([^}]+)\}", text)
    assert block is not None
    generated = set(re.findall(r"'([^']+)'", block.group(1)))
    assert generated == DASHBOARD_ROUTES
