from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.issueClient import IssueClient
from kernelCI_app.unitTests.utils.asserts import (
    assert_status_code_and_error_response,
)
from kernelCI_app.utils import string_to_json
import pytest
from http import HTTPStatus


client = IssueClient()


@online
@pytest.mark.parametrize(
    "origin, interval_in_day, status_code, has_error_body",
    [
        ("maestro", 7, HTTPStatus.OK, False),
        ("maestro", -5, HTTPStatus.BAD_REQUEST, True),
        ("invalid origin", 5, HTTPStatus.OK, True),
    ],
)
def test_list(origin, interval_in_day, status_code, has_error_body):
    response = client.get_issues_list(origin=origin, interval_in_days=interval_in_day)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=issues_listing_fields, response_content=content
        )

    if "issues" in content:
        assert_has_fields_in_response_content(
            fields=issues_fields, response_content=content["issues"][0]
        )


@online
@pytest.mark.parametrize(
    "issue_id, issue_version, status_code, has_error_body",
    [
        ("maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573", 1, HTTPStatus.OK, False),
        ("maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573", 0, HTTPStatus.OK, True),
        (
            "maestro:87244933628a2612f39e6096115454f1e8bb3e1c",
            None,
            HTTPStatus.OK,
            False,
        ),
    ],
)
def test_details(issue_id, issue_version, status_code, has_error_body):
    response = client.get_issues_details(issue_id=issue_id, issue_version=issue_version)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )


@online
@pytest.mark.parametrize(
    "issues_list, status_code, has_error_body",
    [
        (None, HTTPStatus.BAD_REQUEST, True),
        ([], HTTPStatus.BAD_REQUEST, True),
        (
            [
                ["maestro:ee1cba21ee3fe47f21061725de689b638a9c431a", 1],
                ["maestro:cb38e75d16f267781d5b085b9b2dbb390e2885c4", 1],
            ],
            HTTPStatus.OK,
            False,
        ),
        (
            [
                ["maestro:ee1cba21ee3fe47f21061725de689b638a9c431a", 1],
                ["maestro:cb38e75d16f267781d5b085b9b2dbb390e2885c4", 1],
                ["invalid id", 1],
            ],
            HTTPStatus.OK,
            False,
        ),
    ],
)
def test_extra_details(issues_list, status_code, has_error_body):
    response = client.get_issues_extra(issues_list=issues_list)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )


@online
@pytest.mark.parametrize(
    "issue_id, issue_version, status_code, has_error_body",
    [
        ("maestro:ae160f6f27192c3527b2e88faba35d85d27c285f", 1, HTTPStatus.OK, False),
        ("maestro:b9856de6a9d2099f438c8946f3ba192e046bda35", 1, HTTPStatus.OK, True),
        ("maestro:b9856de6a9d2099f438c8946f3ba192e046bda35", None, HTTPStatus.OK, True),
    ],
)
def test_issue_tests(issue_id, issue_version, status_code, has_error_body):
    response = client.get_issue_tests(issue_id=issue_id, issue_version=issue_version)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=test_fields, response_content=content[0]
        )


@online
@pytest.mark.parametrize(
    "issue_id, issue_version, status_code, has_error_body",
    [
        ("maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573", 1, HTTPStatus.OK, False),
        ("maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573", 0, HTTPStatus.OK, True),
        (
            "maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573",
            None,
            HTTPStatus.OK,
            False,
        ),
    ],
)
def test_issue_builds(issue_id, issue_version, status_code, has_error_body):
    response = client.get_issue_builds(issue_id=issue_id, issue_version=issue_version)
    content = string_to_json(response.content.decode())
    assert_status_code_and_error_response(
        response=response,
        content=content,
        status_code=status_code,
        should_error=has_error_body,
    )

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=build_field, response_content=content[0]
        )
