from http import HTTPStatus

import pytest
from django.urls import reverse

import requests
from kernelCI_app.tests.utils.asserts import (
    assert_has_fields_in_response_content,
    assert_status_code_and_error_response,
)
from kernelCI_app.tests.utils.client.baseClient import BaseClient
from kernelCI_app.utils import string_to_json

LAB_FIELDS = [
    "lab_name",
    "build_status_summary",
    "boot_status_summary",
    "test_status_summary",
]
STATUS_FIELDS = ["PASS", "FAIL", "INCONCLUSIVE"]


@pytest.mark.parametrize(
    "query, status_code, has_error_body",
    [
        (
            {"origin": "maestro", "interval_in_days": "7"},
            HTTPStatus.OK,
            False,
        ),
        (
            {"origin": "invalid", "interval_in_days": "7"},
            HTTPStatus.OK,
            True,
        ),
        (
            {"origin": "maestro", "interval_in_days": "-1"},
            HTTPStatus.BAD_REQUEST,
            True,
        ),
    ],
)
def test_lab_listing(
    query: dict,
    status_code: HTTPStatus,
    has_error_body: bool,
) -> None:
    url = BaseClient().get_endpoint(path=reverse("labs"), query=query)
    response = requests.get(url)
    content = string_to_json(response.content.decode())

    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if has_error_body:
        return

    lab = content["labs"][0]
    assert_has_fields_in_response_content(
        fields=LAB_FIELDS,
        response_content=lab,
    )
    for summary in (
        lab["build_status_summary"],
        lab["boot_status_summary"],
        lab["test_status_summary"],
    ):
        assert_has_fields_in_response_content(
            fields=STATUS_FIELDS,
            response_content=summary,
        )
