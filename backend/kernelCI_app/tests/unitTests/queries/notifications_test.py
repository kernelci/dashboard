from unittest.mock import MagicMock, patch

from kernelCI_app.queries.notifications import (
    kcidb_new_issues,
    kcidb_issue_details,
    kcidb_build_incidents,
    kcidb_test_incidents,
    kcidb_last_test_without_issue,
    get_checkout_summary_data,
    kcidb_tests_results,
    get_issues_summary_data,
    kcidb_execute_query,
)

from kernelCI_app.tests.unitTests.queries.conftest import setup_mock_cursor


class TestKcidbExecuteQuery:
    @patch("kernelCI_app.queries.notifications.connection")
    def test_kcidb_execute_query_success(self, mock_connection):
        expected_rows = [("test", "PASS", "boot")]
        expected_cols = ["id", "status", "path"]
        mock_cursor = setup_mock_cursor(mock_connection)
        mock_cursor.description = [(col,) for col in expected_cols]
        mock_cursor.fetchall.return_value = expected_rows

        result = kcidb_execute_query("SELECT * FROM tests WHERE id = %s", ["test"])

        assert len(result) == 1
        assert result[0]["id"] == "test"
        assert result[0]["status"] == "PASS"

    @patch("kernelCI_app.queries.notifications.connection")
    def test_kcidb_execute_query_empty_result(self, mock_connection):
        mock_cursor = setup_mock_cursor(mock_connection)
        mock_cursor.fetchall.return_value = []

        result = kcidb_execute_query(
            "SELECT * FROM tests WHERE id = %s", ["nonexistent"]
        )

        assert result == []

    @patch("kernelCI_app.queries.notifications.connection")
    @patch("kernelCI_app.queries.notifications.sys")
    def test_kcidb_execute_query_exception(self, mock_sys, mock_connection):
        mock_cursor = setup_mock_cursor(mock_connection)
        mock_cursor.execute.side_effect = Exception("Database error")

        kcidb_execute_query("SELECT * FROM tests WHERE id = %s", ["test"])

        mock_sys.exit.assert_called_once()


class TestKcidbNewIssues:
    @patch("kernelCI_app.queries.notifications.kcidb_execute_query")
    def test_kcidb_new_issues_success(self, mock_execute_query):
        expected_result = [{"_timestamp": "2025-11-10T10:00:00Z", "id": "issue"}]
        mock_execute_query.return_value = expected_result

        result = kcidb_new_issues()

        assert result == expected_result
        mock_execute_query.assert_called_once()


class TestKcidbIssueDetails:
    @patch("kernelCI_app.queries.notifications.kcidb_execute_query")
    def test_kcidb_issue_details_success(self, mock_execute_query):
        expected_result = [{"_timestamp": "2025-11-10T10:00:00Z", "id": "issue"}]
        mock_execute_query.return_value = expected_result

        result = kcidb_issue_details("issue")

        assert result == expected_result
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        assert "%(issue_id)s" in call_args[0][0]
        assert call_args[0][1]["issue_id"] == "issue"


class TestKcidbBuildIncidents:
    @patch("kernelCI_app.queries.notifications.kcidb_execute_query")
    def test_kcidb_build_incidents_success(self, mock_execute_query):
        expected_result = [{"id": "build", "config_name": "defconfig"}]
        mock_execute_query.return_value = expected_result

        result = kcidb_build_incidents("issue")

        assert result == expected_result
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        assert "%(issue_id)s" in call_args[0][0]
        assert call_args[0][1]["issue_id"] == "issue"


class TestKcidbTestIncidents:
    @patch("kernelCI_app.queries.notifications.kcidb_execute_query")
    def test_kcidb_test_incidents_success(self, mock_execute_query):
        expected_result = [{"id": "test", "path": "boot"}]
        mock_execute_query.return_value = expected_result

        result = kcidb_test_incidents("issue")

        assert result == expected_result
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        assert "%(issue_id)s" in call_args[0][0]
        assert call_args[0][1]["issue_id"] == "issue"


class TestKcidbLastTestWithoutIssue:
    @patch("kernelCI_app.queries.notifications.kcidb_execute_query")
    def test_kcidb_last_test_without_issue_success(self, mock_execute_query):
        issue = {
            "id": "issue",
            "git_repository_url": "https://my_url.com",
            "git_repository_branch": "master",
        }
        incident = {
            "path": "boot",
            "platform": "x86_64",
            "oldest_timestamp": "2025-11-11T10:00:00Z",
        }
        expected_result = [{"id": "test", "start_time": "2025-11-11T10:00:00Z"}]
        mock_execute_query.return_value = expected_result

        result = kcidb_last_test_without_issue(issue, incident)

        assert result == expected_result
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        assert "%(giturl)s" in query
        assert "%(branch)s" in query
        assert params["giturl"] == issue["git_repository_url"]
        assert params["branch"] == issue["git_repository_branch"]
        assert params["path"] == incident["path"]
        assert params["platform"] == incident["platform"]


class TestGetCheckoutSummaryData:
    @patch("kernelCI_app.queries.notifications.get_tree_listing_query")
    @patch("kernelCI_app.queries.notifications.dict_fetchall")
    @patch("kernelCI_app.queries.notifications.connection")
    def test_get_checkout_summary_data_success(
        self, mock_connection, mock_dict_fetchall, mock_get_tree_query
    ):
        expected_result = [{"checkout_id": "checkout", "tree_name": "mainline"}]
        mock_get_tree_query.return_value = "SELECT * FROM checkouts"
        mock_dict_fetchall.return_value = expected_result
        setup_mock_cursor(mock_connection)

        result = get_checkout_summary_data(
            tuple_params=[("master", "https://my_url.com", "maestro")]
        )

        assert result == expected_result

    @patch("kernelCI_app.queries.notifications.get_tree_listing_query")
    def test_get_checkout_summary_data_empty_params(self, mock_get_tree_query):
        result = get_checkout_summary_data(tuple_params=[])

        assert result == []
        mock_get_tree_query.assert_not_called()


class TestKcidbTestsResults:
    @patch("kernelCI_app.queries.notifications.dict_fetchall")
    @patch("kernelCI_app.queries.notifications.connection")
    def test_kcidb_tests_results_success(self, mock_connection, mock_dict_fetchall):
        expected_result = [{"id": "test", "path": "boot", "status": "PASS"}]
        mock_dict_fetchall.return_value = expected_result
        setup_mock_cursor(mock_connection)

        result = kcidb_tests_results(
            origin="maestro",
            giturl="https://my_url.com",
            branch="master",
            hash="abc123",
            paths=["boot"],
            interval="7 days",
            group_size=10,
        )

        assert result == expected_result

    @patch("kernelCI_app.queries.notifications.dict_fetchall")
    @patch("kernelCI_app.queries.notifications.connection")
    def test_kcidb_tests_results_multiple_paths(
        self, mock_connection, mock_dict_fetchall
    ):
        expected_result = [
            {"id": "test_1", "path": "boot", "status": "PASS"},
            {"id": "test_2", "path": "boot.nfs", "status": "FAIL"},
        ]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = setup_mock_cursor(mock_connection)

        result = kcidb_tests_results(
            origin="maestro",
            giturl="https://my_url.com",
            branch="master",
            hash="abc123",
            paths=["boot", "boot.nfs", "ltp"],
            interval="7 days",
            group_size=10,
        )

        assert result == expected_result
        execute_call = mock_cursor.execute.call_args
        query = execute_call[0][0]
        assert "OR t.path LIKE" in query

    @patch("kernelCI_app.queries.notifications.dict_fetchall")
    @patch("kernelCI_app.queries.notifications.connection")
    def test_kcidb_tests_results_with_empty_paths_list(
        self, mock_connection, mock_dict_fetchall
    ):
        mock_dict_fetchall.return_value = []
        setup_mock_cursor(mock_connection)

        result = kcidb_tests_results(
            origin="maestro",
            giturl="https://my_url.com",
            branch="master",
            hash="abc123",
            paths=[],
            interval="7 days",
            group_size=10,
        )

        assert result == []


class TestGetIssuesSummaryData:
    @patch("kernelCI_app.queries.notifications.dict_fetchall")
    @patch("kernelCI_app.queries.notifications.connections")
    def test_get_issues_summary_data_success(
        self, mock_connections, mock_dict_fetchall
    ):
        expected_result = [{"checkout_id": "checkout_1", "issue_id": "issue_1"}]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = MagicMock()
        mock_connections.__getitem__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        result = get_issues_summary_data(checkout_ids=["checkout_1", "checkout_2"])

        assert result == expected_result

    def test_get_issues_summary_data_empty_list(self):
        result = get_issues_summary_data(checkout_ids=[])

        assert result == []
