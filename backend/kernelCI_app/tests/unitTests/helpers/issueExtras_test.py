from datetime import datetime
from unittest.mock import patch

from kernelCI_app.helpers.issueExtras import (
    TagUrls,
    assign_issue_incidents,
    assign_issue_trees,
    process_issues_extra_details,
)
from kernelCI_app.typeModels.issues import (
    ExtraIssuesData,
    Incident,
    IssueWithExtraInfo,
)


class TestProcessIssuesExtraDetails:
    @patch("kernelCI_app.helpers.issueExtras.assign_issue_incidents")
    @patch("kernelCI_app.helpers.issueExtras.assign_issue_trees")
    def test_process_issues_extra_details_with_issues(
        self, mock_assign_trees, mock_assign_incidents
    ):
        """Test process_issues_extra_details with issues."""
        issue_key_list = [("issue1", 1), ("issue2", 2)]
        processed_issues_table = {}

        process_issues_extra_details(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        mock_assign_incidents.assert_called_once_with(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )
        mock_assign_trees.assert_called_once_with(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

    @patch("kernelCI_app.helpers.issueExtras.assign_issue_incidents")
    @patch("kernelCI_app.helpers.issueExtras.assign_issue_trees")
    def test_process_issues_extra_details_empty_list(
        self, mock_assign_trees, mock_assign_incidents
    ):
        """Test process_issues_extra_details with empty issue list."""
        issue_key_list = []
        processed_issues_table = {}

        process_issues_extra_details(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        mock_assign_incidents.assert_not_called()
        mock_assign_trees.assert_not_called()


class TestAssignIssueFirstSeen:
    @patch("kernelCI_app.helpers.issueExtras.get_issue_next_checkout_data")
    @patch("kernelCI_app.helpers.issueExtras.get_issue_last_seen_data")
    @patch("kernelCI_app.helpers.issueExtras.get_issue_first_seen_data")
    def test_assign_issue_first_seen_with_data(
        self, mock_get_first_data, mock_get_last_data, mock_get_next_checkout
    ):
        """Test assign_issue_incidents with data."""
        mock_get_first_data.return_value = [
            {
                "issue_id": "issue1",
                "first_seen": "2024-01-15T10:00:00Z",
                "git_commit_hash": "abc123",
                "git_repository_url": TagUrls.MAINLINE_URL,
                "git_repository_branch": "master",
                "git_commit_name": "commit1",
                "tree_name": "mainline",
                "issue_version": 1,
                "checkout_id": "checkout1",
            }
        ]
        mock_get_last_data.return_value = [
            {
                "issue_id": "issue1",
                "first_seen": "2024-06-15T10:00:00Z",
                "git_commit_hash": "xyz789",
                "git_repository_url": TagUrls.MAINLINE_URL,
                "git_repository_branch": "master",
                "git_commit_name": "commit_last",
                "tree_name": "mainline",
                "issue_version": 2,
                "checkout_id": "checkout2",
            }
        ]
        mock_get_next_checkout.return_value = [
            {
                "issue_id": "issue1",
                "checkout_id": "checkout_next",
                "start_time": "2024-06-16T10:00:00Z",
                "git_commit_hash": "next123",
                "git_commit_name": "commit_next",
                "git_repository_url": TagUrls.MAINLINE_URL,
                "git_repository_branch": "master",
                "tree_name": "mainline",
                "origin": "maestro",
            }
        ]

        issue_key_list = [("issue1", 1)]
        processed_issues_table = {}

        assign_issue_incidents(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        mock_get_first_data.assert_called_once_with(issue_id_list=["issue1"])
        mock_get_last_data.assert_called_once_with(issue_id_list=["issue1"])
        mock_get_next_checkout.assert_called_once_with(issue_id_list=["issue1"])

        assert "issue1" in processed_issues_table
        issue_data = processed_issues_table["issue1"]
        assert isinstance(issue_data, ExtraIssuesData)
        assert issue_data.first_incident.first_seen == datetime.fromisoformat(
            "2024-01-15T10:00:00Z"
        )
        assert issue_data.first_incident.git_commit_hash == "abc123"
        assert issue_data.last_incident.git_commit_hash == "xyz789"
        assert issue_data.next_checkout is not None
        assert issue_data.next_checkout.checkout_id == "checkout_next"
        assert issue_data.next_checkout.git_commit_hash == "next123"
        assert 1 in issue_data.versions

    @patch("kernelCI_app.helpers.issueExtras.get_issue_next_checkout_data")
    @patch("kernelCI_app.helpers.issueExtras.get_issue_last_seen_data")
    @patch("kernelCI_app.helpers.issueExtras.get_issue_first_seen_data")
    def test_assign_issue_incidents_with_multiple_versions(
        self, mock_get_first_data, mock_get_last_data, mock_get_next_checkout
    ):
        """Test assign_issue_incidents with multiple versions."""
        mock_get_first_data.return_value = [
            {
                "issue_id": "issue1",
                "first_seen": "2024-01-15T10:00:00Z",
                "git_commit_hash": "abc123",
                "git_repository_url": TagUrls.MAINLINE_URL,
                "git_repository_branch": "master",
                "git_commit_name": "commit1",
                "tree_name": "mainline",
                "issue_version": 1,
                "checkout_id": "checkout1",
            }
        ]
        mock_get_last_data.return_value = mock_get_first_data.return_value
        mock_get_next_checkout.return_value = []

        issue_key_list = [("issue1", 1), ("issue1", 2)]
        processed_issues_table = {}

        assign_issue_incidents(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        issue_data = processed_issues_table["issue1"]

        assert issue_data.first_incident.first_seen == datetime.fromisoformat(
            "2024-01-15T10:00:00Z"
        )
        assert issue_data.first_incident.git_commit_hash == "abc123"
        assert issue_data.first_incident.issue_version == 1
        assert issue_data.next_checkout is None
        assert 1 in issue_data.versions
        assert 2 in issue_data.versions
        assert issue_data.versions[1] is None
        assert issue_data.versions[2] is None

    @patch("kernelCI_app.helpers.issueExtras.get_issue_next_checkout_data")
    @patch("kernelCI_app.helpers.issueExtras.get_issue_last_seen_data")
    @patch("kernelCI_app.helpers.issueExtras.get_issue_first_seen_data")
    def test_assign_issue_incidents_with_multiple_issues(
        self, mock_get_first_data, mock_get_last_data, mock_get_next_checkout
    ):
        """Test assign_issue_incidents with multiple issues."""
        mock_get_first_data.return_value = [
            {
                "issue_id": "issue1",
                "first_seen": "2024-01-15T10:00:00Z",
                "git_commit_hash": "abc123",
                "git_repository_url": TagUrls.MAINLINE_URL,
                "git_repository_branch": "master",
                "git_commit_name": "commit1",
                "tree_name": "mainline",
                "issue_version": 1,
                "checkout_id": "checkout1",
            },
            {
                "issue_id": "issue2",
                "first_seen": "2024-01-16T10:00:00Z",
                "git_commit_hash": "def456",
                "git_repository_url": TagUrls.STABLE_URL,
                "git_repository_branch": "linux-5.4.y",
                "git_commit_name": "commit2",
                "tree_name": "stable",
                "issue_version": 1,
                "checkout_id": "checkout2",
            },
        ]
        mock_get_last_data.return_value = mock_get_first_data.return_value
        mock_get_next_checkout.return_value = []

        issue_key_list = [("issue1", 1), ("issue2", 1)]
        processed_issues_table = {}

        assign_issue_incidents(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        assert "issue1" in processed_issues_table
        assert "issue2" in processed_issues_table
        assert len(processed_issues_table) == 2

    @patch("kernelCI_app.helpers.issueExtras.get_issue_next_checkout_data")
    @patch("kernelCI_app.helpers.issueExtras.get_issue_last_seen_data")
    @patch("kernelCI_app.helpers.issueExtras.get_issue_first_seen_data")
    def test_assign_issue_incidents_no_data(
        self, mock_get_first_data, mock_get_last_data, mock_get_next_checkout
    ):
        """Test assign_issue_incidents with no data."""
        mock_get_first_data.return_value = []
        mock_get_last_data.return_value = []
        mock_get_next_checkout.return_value = []

        issue_key_list = [("issue1", 1)]
        processed_issues_table = {}

        assign_issue_incidents(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        assert len(processed_issues_table) == 0
        mock_get_next_checkout.assert_called_once_with(issue_id_list=["issue1"])


class TestAssignIssueTrees:
    @patch("kernelCI_app.helpers.issueExtras.get_issue_trees_data")
    def test_assign_issue_trees_with_data(self, mock_get_data):
        """Test assign_issue_trees with data."""
        mock_get_data.return_value = [
            {
                "issue_id": "issue1",
                "issue_version": 1,
                "git_repository_url": TagUrls.MAINLINE_URL,
                "git_repository_branch": "master",
                "tree_name": "mainline",
            }
        ]

        issue_key_list = [("issue1", 1)]
        processed_issues_table = {
            "issue1": ExtraIssuesData(
                first_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                last_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                versions={1: None},
            )
        }

        assign_issue_trees(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        mock_get_data.assert_called_once_with(issue_key_list=issue_key_list)

        issue_data = processed_issues_table["issue1"]
        version_data = issue_data.versions[1]
        assert isinstance(version_data, IssueWithExtraInfo)
        assert "mainline" in version_data.tags
        assert len(version_data.trees) == 1
        assert version_data.trees[0].tree_name == "mainline"
        assert version_data.trees[0].git_repository_branch == "master"

    @patch("kernelCI_app.helpers.issueExtras.get_issue_trees_data")
    def test_assign_issue_trees_with_stable_tag(self, mock_get_data):
        """Test assign_issue_trees with stable tag."""
        mock_get_data.return_value = [
            {
                "issue_id": "issue1",
                "issue_version": 1,
                "git_repository_url": TagUrls.STABLE_URL,
                "git_repository_branch": "linux-5.4.y",
                "tree_name": "stable",
            }
        ]

        issue_key_list = [("issue1", 1)]
        processed_issues_table = {
            "issue1": ExtraIssuesData(
                first_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.STABLE_URL,
                    git_repository_branch="linux-5.4.y",
                    git_commit_name="commit1",
                    tree_name="stable",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                last_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                versions={1: None},
            )
        }

        assign_issue_trees(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        issue_data = processed_issues_table["issue1"]
        version_data = issue_data.versions[1]
        assert "stable" in version_data.tags

    @patch("kernelCI_app.helpers.issueExtras.get_issue_trees_data")
    def test_assign_issue_trees_with_linux_next_tag(self, mock_get_data):
        """Test assign_issue_trees with linux-next tag."""
        mock_get_data.return_value = [
            {
                "issue_id": "issue1",
                "issue_version": 1,
                "git_repository_url": TagUrls.LINUX_NEXT_URL,
                "git_repository_branch": "master",
                "tree_name": "linux-next",
            }
        ]

        issue_key_list = [("issue1", 1)]
        processed_issues_table = {
            "issue1": ExtraIssuesData(
                first_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.LINUX_NEXT_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="linux-next",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                last_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                versions={1: None},
            )
        }

        assign_issue_trees(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        issue_data = processed_issues_table["issue1"]
        version_data = issue_data.versions[1]
        assert "linux-next" in version_data.tags

    @patch("kernelCI_app.helpers.issueExtras.get_issue_trees_data")
    def test_assign_issue_trees_with_pending_fixes_branch(self, mock_get_data):
        """Test assign_issue_trees with pending-fixes branch."""
        mock_get_data.return_value = [
            {
                "issue_id": "issue1",
                "issue_version": 1,
                "git_repository_url": TagUrls.LINUX_NEXT_URL,
                "git_repository_branch": "pending-fixes",
                "tree_name": "linux-next",
            }
        ]

        issue_key_list = [("issue1", 1)]
        processed_issues_table = {
            "issue1": ExtraIssuesData(
                first_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.LINUX_NEXT_URL,
                    git_repository_branch="pending-fixes",
                    git_commit_name="commit1",
                    tree_name="linux-next",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                last_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                versions={1: None},
            )
        }

        assign_issue_trees(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        issue_data = processed_issues_table["issue1"]
        version_data = issue_data.versions[1]
        assert "linux-next" in version_data.tags

    @patch("kernelCI_app.helpers.issueExtras.get_issue_trees_data")
    def test_assign_issue_trees_with_none_tree_name(self, mock_get_data):
        """Test assign_issue_trees with None tree_name."""
        mock_get_data.return_value = [
            {
                "issue_id": "issue1",
                "issue_version": 1,
                "git_repository_url": TagUrls.MAINLINE_URL,
                "git_repository_branch": "master",
                "tree_name": None,
            }
        ]

        issue_key_list = [("issue1", 1)]
        processed_issues_table = {
            "issue1": ExtraIssuesData(
                first_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                last_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                versions={1: None},
            )
        }

        assign_issue_trees(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        issue_data = processed_issues_table["issue1"]
        version_data = issue_data.versions[1]
        assert len(version_data.trees) == 0
        assert "mainline" in version_data.tags

    @patch("kernelCI_app.helpers.issueExtras.get_issue_trees_data")
    def test_assign_issue_trees_with_none_branch(self, mock_get_data):
        """Test assign_issue_trees with None branch."""
        mock_get_data.return_value = [
            {
                "issue_id": "issue1",
                "issue_version": 1,
                "git_repository_url": TagUrls.MAINLINE_URL,
                "git_repository_branch": None,
                "tree_name": "mainline",
            }
        ]

        issue_key_list = [("issue1", 1)]
        processed_issues_table = {
            "issue1": ExtraIssuesData(
                first_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                last_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                versions={1: None},
            )
        }

        assign_issue_trees(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        issue_data = processed_issues_table["issue1"]
        version_data = issue_data.versions[1]
        assert len(version_data.trees) == 0
        assert len(version_data.tags) == 0

    @patch("kernelCI_app.helpers.issueExtras.get_issue_trees_data")
    @patch("kernelCI_app.helpers.issueExtras.log_message")
    def test_assign_issue_trees_with_missing_issue(
        self, mock_log_message, mock_get_data
    ):
        """Test assign_issue_trees with missing issue in processed_issues_table."""
        mock_get_data.return_value = [
            {
                "issue_id": "issue1",
                "issue_version": 1,
                "git_repository_url": TagUrls.MAINLINE_URL,
                "git_repository_branch": "master",
                "tree_name": "mainline",
            }
        ]

        issue_key_list = [("issue1", 1)]
        processed_issues_table = {}

        assign_issue_trees(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        mock_log_message.assert_called_once()
        assert (
            "Got record for issue without incident" in mock_log_message.call_args[0][0]
        )

    @patch("kernelCI_app.helpers.issueExtras.get_issue_trees_data")
    def test_assign_issue_trees_with_missing_version(self, mock_get_data):
        """Test assign_issue_trees with missing version."""
        mock_get_data.return_value = [
            {
                "issue_id": "issue1",
                "issue_version": 2,
                "git_repository_url": TagUrls.MAINLINE_URL,
                "git_repository_branch": "master",
                "tree_name": "mainline",
            }
        ]

        issue_key_list = [("issue1", 1)]
        processed_issues_table = {
            "issue1": ExtraIssuesData(
                first_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                last_incident=Incident(
                    first_seen="2024-01-15T10:00:00Z",
                    git_commit_hash="abc123",
                    git_repository_url=TagUrls.MAINLINE_URL,
                    git_repository_branch="master",
                    git_commit_name="commit1",
                    tree_name="mainline",
                    issue_version=1,
                    checkout_id="checkout1",
                ),
                versions={1: None},
            )
        }

        assign_issue_trees(
            issue_key_list=issue_key_list, processed_issues_table=processed_issues_table
        )

        assert 2 in processed_issues_table["issue1"].versions
        version_data = processed_issues_table["issue1"].versions[2]
        assert isinstance(version_data, IssueWithExtraInfo)
        assert version_data.id == "issue1"
        assert version_data.version == 2
