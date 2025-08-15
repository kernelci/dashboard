import pytest
from kernelCI_app.helpers.filters import should_filter_test_issue
from kernelCI_app.constants.general import UNCATEGORIZED_STRING


@pytest.mark.unit
class TestShouldFilterTestIssue:
    def test_no_issue_filters(self):
        assert not should_filter_test_issue(
            issue_filters=set(),
            issue_id=UNCATEGORIZED_STRING,
            issue_version=None,
            incident_test_id="incident_test_1",
        )

    def test_unknown_filter_with_exclusively_build_issue(self):
        assert should_filter_test_issue(
            issue_filters={UNCATEGORIZED_STRING},
            issue_id="issue1",
            issue_version=1,
            incident_test_id="incident_test_1",
        )

    def test_unknown_issue_but_not_from_test(self):
        assert not should_filter_test_issue(
            issue_filters={UNCATEGORIZED_STRING},
            issue_id="maestro:72697a4efbbd0eff7080781839b405bbf0902f79",
            issue_version=0,
            incident_test_id=None,
        )
