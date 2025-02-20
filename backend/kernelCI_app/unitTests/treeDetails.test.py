import unittest
from kernelCI_app.helpers.filters import should_filter_test_issue
from kernelCI_app.constants.general import UNKNOWN_STRING


# TODO: replace with pytest
class TestShouldFilterTestIssue(unittest.TestCase):

    def test_no_issue_filters(self):
        self.assertFalse(
            should_filter_test_issue(
                issue_filters=set(),
                issue_id=UNKNOWN_STRING,
                issue_version=None,
                incident_test_id="incident_test_1",
                test_status="FAIL",
            )
        )

    def test_unknown_filter_with_exclusively_build_issue(self):
        self.assertTrue(
            should_filter_test_issue(
                issue_filters={UNKNOWN_STRING},
                issue_id="issue1",
                issue_version=1,
                incident_test_id="incident_test_1",
                test_status="PASS",
            )
        )

    def test_unknown_issue_but_not_from_test(self):
        self.assertFalse(
            should_filter_test_issue(
                issue_filters={UNKNOWN_STRING},
                issue_id="maestro:72697a4efbbd0eff7080781839b405bbf0902f79",
                issue_version=0,
                incident_test_id=None,
                test_status="FAIL",
            )
        )


if __name__ == "__main__":
    unittest.main()
