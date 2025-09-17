"""
Issue data management class.
"""

from .fixtures import ISSUE_TEST_DATA


class Issue:
    """Manages issue test data and operations."""

    @classmethod
    def get_issue_data(cls, issue_id: str):
        """Get complete issue data by ID."""
        return ISSUE_TEST_DATA.get(issue_id)

    @classmethod
    def get_issue_build_ids(cls, issue_id: str):
        """Get build IDs associated with an issue."""
        issue_data = ISSUE_TEST_DATA.get(issue_id)
        return issue_data.get("build_ids", []) if issue_data else []

    @classmethod
    def get_issue_test_ids(cls, issue_id: str):
        """Get test IDs associated with an issue."""
        issue_data = ISSUE_TEST_DATA.get(issue_id)
        return issue_data.get("test_ids", []) if issue_data else []

    @classmethod
    def get_issues_with_builds(cls):
        """Get all issues that have build incidents."""
        return {
            issue_id: issue_data
            for issue_id, issue_data in ISSUE_TEST_DATA.items()
            if issue_data.get("build_ids")
        }

    @classmethod
    def get_issues_with_tests(cls):
        """Get all issues that have test incidents."""
        return {
            issue_id: issue_data
            for issue_id, issue_data in ISSUE_TEST_DATA.items()
            if issue_data.get("test_ids")
        }

    @classmethod
    def get_all_issue_ids(cls):
        """Get all issue IDs from ISSUE_TEST_DATA."""
        return list(ISSUE_TEST_DATA.keys())

    @classmethod
    def is_known_issue(cls, issue_id: str):
        """Check if an issue ID exists in ISSUE_TEST_DATA."""
        return issue_id in ISSUE_TEST_DATA
