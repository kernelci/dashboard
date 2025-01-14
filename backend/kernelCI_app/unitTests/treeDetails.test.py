import unittest
from kernelCI_app.helpers.filters import should_filter_test_issue, UNKNOWN_STRING


# TODO: replace with pytest
class TestShouldFilterTestIssue(unittest.TestCase):

    def test_no_issue_filters(self):
        self.assertFalse(
            should_filter_test_issue(set(), UNKNOWN_STRING, "incident_test_1", "FAIL")
        )

    def test_unknown_filter_with_exclusively_build_issue(self):
        self.assertTrue(
            should_filter_test_issue(
                {UNKNOWN_STRING}, "issue1", "incident_test_1", "PASS"
            )
        )

    def test_unknown_issue_but_not_from_test(self):
        self.assertFalse(
            should_filter_test_issue(
                {UNKNOWN_STRING},
                "maestro:72697a4efbbd0eff7080781839b405bbf0902f79",
                None,
                "FAIL",
            )
        )


if __name__ == "__main__":
    unittest.main()
