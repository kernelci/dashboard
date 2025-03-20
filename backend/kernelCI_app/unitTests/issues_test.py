from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.client.issueClient import IssueClient
from kernelCI_app.unitTests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.unitTests.utils.fields.issues import (
    issues_expected_fields,
    issues_listing_fields,
)
from kernelCI_app.unitTests.utils.fields.tests import issue_tests_expected_fields
from kernelCI_app.unitTests.utils.fields.builds import build_details_expected_fields
from kernelCI_app.utils import string_to_json
import pytest
from http import HTTPStatus


client = IssueClient()

CULPRIT_CODE = {
    "culpritCode": True,
    "excludes_fields": ["culprit_tool", "culprit_harness"],
}

CULPRIT_TOOL = {
    "culpritTool": True,
    "excludes_fields": ["culprit_code", "culprit_harness"],
}

CULPRIT_HARNESS = {
    "culpritHarness": True,
    "excludes_fields": ["culprit_code", "culprit_tool"],
}

CULPRIT_CODE_AND_TOOL = {
    "culpritCode": True,
    "culpritTool": True,
    "excludes_fields": ["culprit_harness"],
}


def pytest_generate_tests(metafunc):
    issues_listing_base_cases = [
        (5, CULPRIT_CODE, HTTPStatus.OK, False),
        (5, CULPRIT_TOOL, HTTPStatus.OK, False),
        (5, CULPRIT_HARNESS, HTTPStatus.OK, False),
        (-5, None, HTTPStatus.BAD_REQUEST, True),
    ]

    if metafunc.config.getoption("--run-all"):
        issues_listing_base_cases += [
            (5, CULPRIT_CODE_AND_TOOL, HTTPStatus.OK, False),
            (5, None, HTTPStatus.OK, False),
        ]

    if "issue_listing_input" in metafunc.fixturenames:
        metafunc.parametrize("issue_listing_input", issues_listing_base_cases)


@online
def test_list(pytestconfig, issue_listing_input):
    interval_in_day, culprit_data, status_code, has_error_body = issue_listing_input
    response = client.get_issues_list(
        interval_in_days=interval_in_day, culprit_data=culprit_data
    )
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

        assert_has_fields_in_response_content(
            fields=issues_expected_fields, response_content=content["issues"][0]
        )

        if culprit_data is not None:
            for culprit in culprit_data["excludes_fields"]:
                assert not content["issues"][0][culprit]

            if pytestconfig.getoption("--run-all") and len(content["issues"]) > 1:
                for culprit in culprit_data["excludes_fields"]:
                    for issue in content["issues"][1:]:
                        assert not issue[culprit]


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

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=issues_expected_fields, response_content=content
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

    if not has_error_body:
        assert_has_fields_in_response_content(
            fields=["issues"], response_content=content
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
            fields=issue_tests_expected_fields, response_content=content[0]
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
            fields=build_details_expected_fields, response_content=content[0]
        )
