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

# Snapshot from: curl -s http://localhost:8000/api/metrics/
metrics_expected_fields = [
    "n_trees",
    "n_checkouts",
    "n_builds",
    "n_tests",
    "n_issues",
    "n_incidents",
    "build_incidents_by_origin",
    "top_issues_by_origin",
    "lab_maps",
    "prev_n_trees",
    "prev_n_checkouts",
    "prev_n_builds",
    "prev_n_tests",
    "prev_lab_maps",
]

metrics_expected_counts = {
    "n_trees": 11,
    "n_checkouts": 58,
    "n_builds": 28,
    "n_tests": 30,
    "n_issues": 20,
    "n_incidents": 8,
    "prev_n_trees": 0,
    "prev_n_checkouts": 0,
    "prev_n_builds": 0,
    "prev_n_tests": 0,
}


def test_get_metrics():
    response = client.get_metrics()
    content = string_to_json(response.content.decode())

    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=HTTPStatus.OK,
        should_error=False,
    )

    assert_has_fields_in_response_content(
        fields=metrics_expected_fields, response_content=content
    )

    for field, expected in metrics_expected_counts.items():
        assert content[field] == expected, (
            f"{field}: api={content[field]} expected={expected}"
        )


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
