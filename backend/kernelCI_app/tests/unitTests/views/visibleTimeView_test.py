import re
from pathlib import Path

import pytest
from prometheus_client import REGISTRY
from rest_framework.test import APIRequestFactory

from kernelCI_app.views.visibleTimeView import DASHBOARD_ROUTES, VisibleTimeView

ROUTE = "/tree/mainline/master"
REPO_ROOT = Path(__file__).resolve().parents[5]


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
        {"route": ROUTE, "time_ms": 86_400_001},
        {"route": ROUTE, "time_ms": "nope"},
        {"time_ms": 20_000},
        {"route": ROUTE},
        {"route": "/nope/not-a-page", "time_ms": 20_000},
    ],
)
def test_invalid_beacon_records_nothing(fields):
    before = _sample("dashboard_route_visible_seconds_count", ROUTE)
    response = _post(fields)
    assert response.status_code == 400
    assert _sample("dashboard_route_visible_seconds_count", ROUTE) == before
    assert _sample("dashboard_route_visible_seconds_count", "/not-a-route") == 0


def test_hardware_paths_are_separate():
    board_a = "/hardware/board-a"
    board_b = "/hardware/board-b"
    before_a = _sample("dashboard_route_visible_seconds_count", board_a)
    before_b = _sample("dashboard_route_visible_seconds_count", board_b)

    first = _post({"route": board_a, "time_ms": 1_000})
    second = _post({"route": board_b, "time_ms": 1_000})

    assert first.status_code == 204
    assert second.status_code == 204
    assert _sample("dashboard_route_visible_seconds_count", board_a) == before_a + 1
    assert _sample("dashboard_route_visible_seconds_count", board_b) == before_b + 1


def test_dashboard_routes_match_generated_route_tree():
    text = (REPO_ROOT / "dashboard/src/routeTree.gen.ts").read_text()
    block = re.search(r"export interface FileRoutesByTo \{([^}]+)\}", text)
    assert block is not None
    generated = set(re.findall(r"'([^']+)'", block.group(1)))
    assert generated == DASHBOARD_ROUTES
