from kernelCI_app.tests.utils.client.issueClient import IssueClient
from kernelCI_app.tests.utils.asserts import (
    assert_status_code_and_error_response,
    assert_has_fields_in_response_content,
)
from kernelCI_app.tests.utils.fields.issues import (
    issues_expected_fields,
    issues_listing_fields,
)
from kernelCI_app.tests.utils.fields.tests import issue_tests_expected_fields
from kernelCI_app.tests.utils.fields.builds import build_details_expected_fields
from kernelCI_app.utils import string_to_json
import pytest
from http import HTTPStatus


client = IssueClient()

DEFAULT_LISTING_STARTING_DATE = "2025-08-15"
DEFAULT_LISTING_INTERVAL_IN_DAYS = 3

CULPRIT_CODE = {
    "filters": {"issue.culprit": "code"},
    "excludes_fields": ["culprit_tool", "culprit_harness"],
}

CULPRIT_TOOL = {
    "filters": {"issue.culprit": "tool"},
    "excludes_fields": ["culprit_code", "culprit_harness"],
}

CULPRIT_HARNESS = {
    "filters": {"issue.culprit": "harness"},
    "excludes_fields": ["culprit_code", "culprit_tool"],
}

CULPRIT_CODE_AND_TOOL = {
    "filters": {
        "issue.culprit": ["code", "tool"],
    },
    "excludes_fields": ["culprit_harness"],
}


def pytest_generate_tests(metafunc):
    issues_listing_base_cases = [
        (
            DEFAULT_LISTING_INTERVAL_IN_DAYS,
            DEFAULT_LISTING_STARTING_DATE,
            CULPRIT_CODE,
            HTTPStatus.OK,
            False,
        ),
        (
            DEFAULT_LISTING_INTERVAL_IN_DAYS,
            DEFAULT_LISTING_STARTING_DATE,
            CULPRIT_TOOL,
            HTTPStatus.OK,
            False,
        ),
        (
            DEFAULT_LISTING_INTERVAL_IN_DAYS,
            DEFAULT_LISTING_STARTING_DATE,
            CULPRIT_HARNESS,
            HTTPStatus.OK,
            False,
        ),
        (
            -5,
            None,
            None,
            HTTPStatus.BAD_REQUEST,
            True,
        ),
    ]

    if metafunc.config.getoption("--run-all"):
        issues_listing_base_cases += [
            (
                DEFAULT_LISTING_INTERVAL_IN_DAYS,
                DEFAULT_LISTING_STARTING_DATE,
                CULPRIT_CODE_AND_TOOL,
                HTTPStatus.OK,
                False,
            ),
            (
                DEFAULT_LISTING_INTERVAL_IN_DAYS,
                DEFAULT_LISTING_STARTING_DATE,
                None,
                HTTPStatus.OK,
                False,
            ),
        ]

    if "issue_listing_input" in metafunc.fixturenames:
        metafunc.parametrize("issue_listing_input", issues_listing_base_cases)


def test_list(pytestconfig, issue_listing_input):
    (
        interval_in_day,
        starting_date_iso_format,
        culprit_data,
        status_code,
        has_error_body,
    ) = issue_listing_input
    filters = culprit_data.get("filters") if culprit_data else None
    response = client.get_issues_list(
        interval_in_days=interval_in_day,
        starting_date_iso_format=starting_date_iso_format,
        filters=filters,
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

        # Even if content exists, all issues might have been filtered out.
        # In that case, we don't need to do further checks.
        if len(content.get("issues", [])) == 0:
            return

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
