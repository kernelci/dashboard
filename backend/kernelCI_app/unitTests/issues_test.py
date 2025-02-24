from kernelCI_app.unitTests.utils.healthCheck import online
from kernelCI_app.unitTests.utils.issueClient import IssueClient
from kernelCI_app.unitTests.utils.defaultTestAsserts import defaultTestAsserts

import pytest

client = IssueClient()


@online
@pytest.mark.parametrize(
    "origin, interval_in_day, status_code, has_error_body",
    [
        ("maestro", 7, 200, False),
        ("maestro", -5, 400, True),
        ("invalid origin", 5, 200, True),
    ],
)
def test_list(origin, interval_in_day, status_code, has_error_body):
    response = client.get_issues_list(origin=origin, interval_in_days=interval_in_day)
    defaultTestAsserts(response, status_code, has_error_body)


@online
@pytest.mark.parametrize(
    "issue_id, issue_version, status_code, has_error_body",
    [
        ("maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573", 1, 200, False),
        ("maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573", 0, 200, True),
        ("maestro:87244933628a2612f39e6096115454f1e8bb3e1c", None, 200, False),
    ],
)
def test_details(issue_id, issue_version, status_code, has_error_body):
    response = client.get_issues_details(issue_id=issue_id, issue_version=issue_version)
    defaultTestAsserts(response, status_code, has_error_body)


@online
@pytest.mark.parametrize(
    "issues_list, status_code, has_error_body",
    [
        (None, 400, True),
        ([], 400, True),
        (
            [
                ["maestro:ee1cba21ee3fe47f21061725de689b638a9c431a", 1],
                ["maestro:cb38e75d16f267781d5b085b9b2dbb390e2885c4", 1],
            ],
            200,
            False,
        ),
        (
            [
                ["maestro:ee1cba21ee3fe47f21061725de689b638a9c431a", 1],
                ["maestro:cb38e75d16f267781d5b085b9b2dbb390e2885c4", 1],
                ["invalid id", 1],
            ],
            200,
            False,
        ),
    ],
)
def test_extra_details(issues_list, status_code, has_error_body):
    response = client.get_issues_extra(issues_list=issues_list)
    defaultTestAsserts(response, status_code, has_error_body)


@online
@pytest.mark.parametrize(
    "issue_id, issue_version, status_code, has_error_body",
    [
        ("maestro:ae160f6f27192c3527b2e88faba35d85d27c285f", 1, 200, False),
        ("maestro:b9856de6a9d2099f438c8946f3ba192e046bda35", 1, 200, True),
        ("maestro:b9856de6a9d2099f438c8946f3ba192e046bda35", None, 400, True),
    ],
)
def test_issue_tests(issue_id, issue_version, status_code, has_error_body):
    response = client.get_issue_tests(issue_id=issue_id, issue_version=issue_version)
    defaultTestAsserts(response, status_code, has_error_body)


@online
@pytest.mark.parametrize(
    "issue_id, issue_version, status_code, has_error_body",
    [
        ("maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573", 1, 200, False),
        ("maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573", 0, 200, True),
        ("maestro:2ff8fe94f6d53f39321d4a37fe15801cedc93573", None, 400, True),
    ],
)
def test_issue_builds(issue_id, issue_version, status_code, has_error_body):
    response = client.get_issue_builds(issue_id=issue_id, issue_version=issue_version)
    defaultTestAsserts(response, status_code, has_error_body)
