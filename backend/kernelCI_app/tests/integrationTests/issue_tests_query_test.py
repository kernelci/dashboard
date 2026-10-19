import pytest

from kernelCI_app.queries.issues import get_issue_tests
from kernelCI_app.tests.factories import IncidentFactory, IssueFactory, TestFactory


@pytest.mark.django_db
def test_get_issue_tests_returns_one_row_when_a_test_is_filed_twice():
    issue = IssueFactory(id="issue-tests-distinct", version=3)
    repeated = TestFactory(id="test-repeated", status="FAIL", path="KUNIT")
    other = TestFactory(id="test-other", status="PASS", path="boot")
    IncidentFactory(issue=issue, test=repeated, build=None)
    IncidentFactory(issue=issue, test=repeated, build=None)
    IncidentFactory(issue=issue, test=other, build=None)

    rows = get_issue_tests(issue_id=issue.id, version=issue.version)

    assert len(rows) == 2
    assert {row["id"] for row in rows} == {repeated.id, other.id}
    by_id = {row["id"]: row for row in rows}
    assert by_id[repeated.id]["status"] == "FAIL"
    assert by_id[repeated.id]["path"] == "KUNIT"
