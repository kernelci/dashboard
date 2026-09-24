from http import HTTPStatus

import pytest

from kernelCI_app.constants.localization import ClientStrings
from kernelCI_app.tests.utils.asserts import (
    assert_has_fields_in_response_content,
    assert_status_code_and_error_response,
)
from kernelCI_app.tests.utils.client.metricsClient import MetricsClient
from kernelCI_app.utils import string_to_json

client = MetricsClient()

metrics_expected_fields = [
    "n_trees",
    "n_checkouts",
    "n_builds",
    "n_tests",
    "n_issues",
    "n_incidents",
    "build_incidents_by_origin",
    "top_issues_by_origin",
    "new_issues_by_origin",
    "lab_maps",
    "prev_n_trees",
    "prev_n_checkouts",
    "prev_n_builds",
    "prev_n_tests",
    "prev_lab_maps",
]

# Plain COUNT(*) fields, additive across disjoint day windows. n_trees is
# COUNT(DISTINCT tree_name), so it does not add up and is excluded here.
additive_count_fields = [
    "n_checkouts",
    "n_builds",
    "n_tests",
    "n_issues",
    "n_incidents",
]


def _ok_content(query: dict[str, str] | None = None) -> dict:
    response = client.get_metrics(query=query)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=HTTPStatus.OK,
        should_error=False,
    )
    return content


metrics_expected_counts = {
    "n_trees": 5,
    "n_checkouts": 21,
    "n_builds": 14,
    "n_tests": 14,
    "n_issues": 7,
    "n_incidents": 7,
    "prev_n_trees": 6,
    "prev_n_checkouts": 20,
    "prev_n_builds": 7,
    "prev_n_tests": 9,
}


def _status(**counts: int) -> dict[str, int]:
    base = {
        "PASS": 0,
        "ERROR": 0,
        "FAIL": 0,
        "SKIP": 0,
        "MISS": 0,
        "DONE": 0,
        "NULL": 0,
    }
    base.update(counts)
    return base


def _lab(
    *,
    covered_builds: int = 0,
    builds: dict[str, int] | None = None,
    boots: dict[str, int] | None = None,
    tests: dict[str, int] | None = None,
) -> dict:
    return {
        "covered_builds": covered_builds,
        "builds": builds if builds is not None else _status(),
        "boots": boots if boots is not None else _status(),
        "tests": tests if tests is not None else _status(),
    }


metrics_expected_lab_maps = {
    "lab-broonie": _lab(builds=_status(FAIL=1)),
    "lab-fake-origin": _lab(
        covered_builds=4,
        builds=_status(SKIP=7),
        tests=_status(SKIP=4),
    ),
    "lab-maestro": _lab(
        covered_builds=8,
        builds=_status(PASS=2, FAIL=3),
        tests=_status(FAIL=6, SKIP=4),
    ),
}

metrics_expected_prev_lab_maps = {
    "lab-broonie": _lab(covered_builds=1, tests=_status(PASS=1)),
    "lab-fake-origin": _lab(covered_builds=2, tests=_status(SKIP=2)),
    "lab-maestro": _lab(
        covered_builds=6,
        builds=_status(PASS=7),
        boots=_status(PASS=1),
        tests=_status(PASS=4, SKIP=1),
    ),
}


def test_get_metrics():
    content = _ok_content()

    assert_has_fields_in_response_content(
        fields=metrics_expected_fields, response_content=content
    )

    for field, expected in metrics_expected_counts.items():
        assert content[field] == expected, (
            f"{field}: api={content[field]} expected={expected}"
        )

    assert content["lab_maps"] == metrics_expected_lab_maps
    assert content["prev_lab_maps"] == metrics_expected_prev_lab_maps


def test_metrics_half_open_windows_tile_exactly():
    """Adjacent half-open windows [start, end) tile without gaps or overlap:
    (2, 0) == (1, 0) + (2, 1) for additive counts."""
    day_1 = _ok_content({"start_days_ago": "1", "end_days_ago": "0"})
    day_2 = _ok_content({"start_days_ago": "2", "end_days_ago": "1"})
    both_days = _ok_content({"start_days_ago": "2", "end_days_ago": "0"})

    for field in additive_count_fields:
        assert both_days[field] == day_1[field] + day_2[field], (
            f"{field}: (2,0)={both_days[field]} != "
            f"(1,0)={day_1[field]} + (2,1)={day_2[field]}"
        )


def test_metrics_window_outside_seeded_range_is_empty():
    """A window entirely beyond the seeded days returns zero counts."""
    content = _ok_content({"start_days_ago": "30", "end_days_ago": "22"})

    for field in additive_count_fields:
        assert content[field] == 0, f"{field}: api={content[field]} expected=0"


@pytest.mark.parametrize(
    "query, status_code, has_error_body",
    [
        (
            {"start_days_ago": "7", "end_days_ago": "7"},
            HTTPStatus.BAD_REQUEST,
            True,
        ),
        (
            {"start_days_ago": "3", "end_days_ago": "7"},
            HTTPStatus.BAD_REQUEST,
            True,
        ),
    ],
)
def test_get_metrics_invalid_interval(query, status_code, has_error_body):
    response = client.get_metrics(query=query)
    content = string_to_json(response.content.decode())

    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )
    assert content.get("error") == ClientStrings.METRICS_INVALID_INTERVAL
