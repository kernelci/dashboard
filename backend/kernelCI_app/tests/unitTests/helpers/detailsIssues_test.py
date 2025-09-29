from unittest.mock import patch, MagicMock
from kernelCI_app.helpers.detailsIssues import sanitize_details_issues_rows
from kernelCI_app.typeModels.issues import Issue


class TestSanitizeDetailsIssuesRows:
    @patch("kernelCI_app.helpers.detailsIssues.create_issue_typed")
    @patch("kernelCI_app.helpers.detailsIssues.convert_issues_dict_to_list_typed")
    def test_sanitize_details_issues_rows_with_single_issue(
        self, mock_convert, mock_create_issue
    ):
        """Test sanitize_details_issues_rows with single issue."""
        mock_issue = MagicMock(spec=Issue)
        mock_create_issue.return_value = mock_issue
        mock_convert.return_value = [mock_issue]

        rows = [
            {
                "id": "issue1",
                "version": 1,
                "comment": "Test comment",
                "report_url": "http://example.com",
                "status": "PASS",
            }
        ]

        result = sanitize_details_issues_rows(rows=rows)

        mock_create_issue.assert_called_once_with(
            issue_id="issue1",
            issue_version=1,
            issue_comment="Test comment",
            issue_report_url="http://example.com",
            starting_count_status="PASS",
        )
        mock_convert.assert_called_once()
        assert result == [mock_issue]

    @patch("kernelCI_app.helpers.detailsIssues.create_issue_typed")
    @patch("kernelCI_app.helpers.detailsIssues.convert_issues_dict_to_list_typed")
    def test_sanitize_details_issues_rows_with_multiple_issues(
        self, mock_convert, mock_create_issue
    ):
        """Test sanitize_details_issues_rows with multiple different issues."""
        mock_issue1 = MagicMock(spec=Issue)
        mock_issue2 = MagicMock(spec=Issue)
        mock_create_issue.side_effect = [mock_issue1, mock_issue2]
        mock_convert.return_value = [mock_issue1, mock_issue2]

        rows = [
            {
                "id": "issue1",
                "version": 1,
                "comment": "Test comment 1",
                "report_url": "http://example.com/1",
                "status": "PASS",
            },
            {
                "id": "issue2",
                "version": 2,
                "comment": "Test comment 2",
                "report_url": "http://example.com/2",
                "status": "FAIL",
            },
        ]

        result = sanitize_details_issues_rows(rows=rows)

        assert mock_create_issue.call_count == 2
        mock_convert.assert_called_once()
        assert result == [mock_issue1, mock_issue2]

    @patch("kernelCI_app.helpers.detailsIssues.create_issue_typed")
    @patch("kernelCI_app.helpers.detailsIssues.convert_issues_dict_to_list_typed")
    def test_sanitize_details_issues_rows_with_duplicate_issue(
        self, mock_convert, mock_create_issue
    ):
        """Test sanitize_details_issues_rows with duplicate issue (same id and version)."""
        mock_issue = MagicMock(spec=Issue)
        mock_issue.incidents_info = MagicMock()
        mock_create_issue.return_value = mock_issue
        mock_convert.return_value = [mock_issue]

        rows = [
            {
                "id": "issue1",
                "version": 1,
                "comment": "Test comment",
                "report_url": "http://example.com",
                "status": "PASS",
            },
            {
                "id": "issue1",
                "version": 1,
                "comment": "Test comment",
                "report_url": "http://example.com",
                "status": "FAIL",
            },
        ]

        result = sanitize_details_issues_rows(rows=rows)

        mock_create_issue.assert_called_once()
        mock_issue.incidents_info.increment.assert_called_once_with("FAIL")
        mock_convert.assert_called_once()
        assert result == [mock_issue]

    @patch("kernelCI_app.helpers.detailsIssues.create_issue_typed")
    @patch("kernelCI_app.helpers.detailsIssues.convert_issues_dict_to_list_typed")
    def test_sanitize_details_issues_rows_with_empty_rows(
        self, mock_convert, mock_create_issue
    ):
        """Test sanitize_details_issues_rows with empty rows list."""
        mock_convert.return_value = []

        result = sanitize_details_issues_rows(rows=[])

        mock_create_issue.assert_not_called()
        mock_convert.assert_called_once()
        assert result == []

    @patch("kernelCI_app.helpers.detailsIssues.create_issue_typed")
    @patch("kernelCI_app.helpers.detailsIssues.convert_issues_dict_to_list_typed")
    def test_sanitize_details_issues_rows_with_none_values(
        self, mock_convert, mock_create_issue
    ):
        """Test sanitize_details_issues_rows with None values in rows."""
        mock_issue = MagicMock(spec=Issue)
        mock_create_issue.return_value = mock_issue
        mock_convert.return_value = [mock_issue]

        rows = [
            {
                "id": "issue1",
                "version": 1,
                "comment": None,
                "report_url": None,
                "status": "PASS",
            }
        ]

        result = sanitize_details_issues_rows(rows=rows)

        mock_create_issue.assert_called_once_with(
            issue_id="issue1",
            issue_version=1,
            issue_comment=None,
            issue_report_url=None,
            starting_count_status="PASS",
        )
        mock_convert.assert_called_once()
        assert result == [mock_issue]
