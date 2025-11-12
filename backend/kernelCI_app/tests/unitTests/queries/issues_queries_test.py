from datetime import datetime
from unittest.mock import MagicMock, patch

from kernelCI_app.queries.issues import (
    get_issue_builds,
    get_issue_tests,
    get_issue_listing_data,
    get_latest_issue_version,
    get_issue_details,
    get_build_issues,
    get_test_issues,
    get_issue_first_seen_data,
    get_issue_trees_data,
)

from kernelCI_app.tests.unitTests.queries.conftest import (
    setup_mock_cursor,
    setup_mock_queryset,
)


class TestGetIssueBuilds:
    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connection")
    def test_get_issue_builds_with_version(self, mock_connection, mock_dict_fetchall):
        expected_result = [{"id": "build", "build_status": "FAIL"}]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = setup_mock_cursor(mock_connection)

        result = get_issue_builds(issue_id="issue", version=1)

        assert result == expected_result
        execute_call = mock_cursor.execute.call_args
        query = execute_call[0][0]
        assert "%(issue_version)s" in query

    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connection")
    def test_get_issue_builds_without_version(
        self, mock_connection, mock_dict_fetchall
    ):
        expected_result = [{"id": "build", "build_status": "FAIL"}]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = setup_mock_cursor(mock_connection)

        result = get_issue_builds(issue_id="issue", version=None)

        assert result == expected_result
        execute_call = mock_cursor.execute.call_args
        query = execute_call[0][0]
        assert "%(issue_version)s" not in query


class TestGetIssueTests:
    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connection")
    def test_get_issue_tests_with_version(self, mock_connection, mock_dict_fetchall):
        expected_result = [{"id": "test", "status": "FAIL"}]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = setup_mock_cursor(mock_connection)

        result = get_issue_tests(issue_id="issue", version=1)

        assert result == expected_result
        execute_call = mock_cursor.execute.call_args
        query = execute_call[0][0]
        assert "%(issue_version)s" in query

    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connection")
    def test_get_issue_tests_without_version(self, mock_connection, mock_dict_fetchall):
        expected_result = [{"id": "test", "status": "FAIL"}]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = setup_mock_cursor(mock_connection)

        result = get_issue_tests(issue_id="issue", version=None)

        assert result == expected_result
        execute_call = mock_cursor.execute.call_args
        query = execute_call[0][0]
        assert "%(issue_version)s" not in query


class TestGetIssueListingData:
    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connection")
    def test_get_issue_listing_data_success(self, mock_connection, mock_dict_fetchall):
        expected_result = [{"id": "issue", "version": 1}]
        mock_dict_fetchall.return_value = expected_result
        setup_mock_cursor(mock_connection)

        result = get_issue_listing_data(
            interval="7 days", starting_date=datetime(2025, 11, 11)
        )

        assert result == expected_result


class TestGetLatestIssueVersion:
    @patch("kernelCI_app.queries.issues.Issues")
    def test_get_latest_issue_version_success(self, mock_issues_model):
        expected_result = {"version": 5}
        setup_mock_queryset(mock_issues_model, expected_result)

        result = get_latest_issue_version(issue_id="issue")

        assert result == expected_result

    @patch("kernelCI_app.queries.issues.Issues")
    def test_get_latest_issue_version_not_found(self, mock_issues_model):
        setup_mock_queryset(mock_issues_model, None)

        result = get_latest_issue_version(issue_id="issue")

        assert result is None


class TestGetIssueDetails:
    @patch("kernelCI_app.queries.issues.Issues")
    def test_get_issue_details_success(self, mock_issues_model):
        expected_result = {"id": "issue", "version": 1}
        setup_mock_queryset(mock_issues_model, expected_result)

        result = get_issue_details(issue_id="issue", version=1)

        assert result == expected_result

    @patch("kernelCI_app.queries.issues.Issues")
    def test_get_issue_details_issue_not_found(self, mock_issues_model):
        mock_queryset = setup_mock_queryset(mock_issues_model, None)

        result = get_issue_details(issue_id="nonexistent", version=1)

        assert result is None
        mock_queryset.filter.assert_called_once_with(id="nonexistent", version=1)

    @patch("kernelCI_app.queries.issues.Issues")
    def test_get_issue_details_version_not_found(self, mock_issues_model):
        mock_queryset = setup_mock_queryset(mock_issues_model, None)

        result = get_issue_details(issue_id="issue", version=999)

        assert result is None
        mock_queryset.filter.assert_called_once_with(id="issue", version=999)


class TestGetBuildIssues:
    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connection")
    def test_get_build_issues_success(self, mock_connection, mock_dict_fetchall):
        expected_result = [{"id": "incident", "issues.id": "issue"}]
        mock_dict_fetchall.return_value = expected_result
        setup_mock_cursor(mock_connection)

        result = get_build_issues(build_id="build")

        assert result == expected_result


class TestGetTestIssues:
    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connection")
    def test_get_test_issues_success(self, mock_connection, mock_dict_fetchall):
        expected_result = [{"id": "incident", "issues.id": "issue"}]
        mock_dict_fetchall.return_value = expected_result
        setup_mock_cursor(mock_connection)

        result = get_test_issues(test_id="test")

        assert result == expected_result


class TestGetIssueFirstSeenData:
    @patch("kernelCI_app.queries.issues.get_query_cache")
    def test_get_issue_first_seen_data_from_cache(self, mock_get_cache):
        issue_id_list = ["issue_1", "issue_2"]
        cached_data = [{"id": "incident_1", "issue_id": "issue_1"}]
        mock_get_cache.return_value = cached_data

        result = get_issue_first_seen_data(issue_id_list=issue_id_list)

        assert result == cached_data

    @patch("kernelCI_app.queries.issues.get_query_cache")
    @patch("kernelCI_app.queries.issues.set_query_cache")
    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connection")
    def test_get_issue_first_seen_data_from_database(
        self, mock_connection, mock_dict_fetchall, mock_set_cache, mock_get_cache
    ):
        mock_get_cache.return_value = None
        expected_result = [{"id": "incident", "issue_id": "issue"}]
        mock_dict_fetchall.return_value = expected_result
        setup_mock_cursor(mock_connection)

        result = get_issue_first_seen_data(issue_id_list=["issue"])

        assert result == expected_result
        mock_set_cache.assert_called_once()

    @patch("kernelCI_app.queries.issues.get_query_cache")
    @patch("kernelCI_app.queries.issues.set_query_cache")
    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connection")
    def test_get_issue_first_seen_data_multiple_issues(
        self, mock_connection, mock_dict_fetchall, mock_set_cache, mock_get_cache
    ):
        mock_get_cache.return_value = None
        expected_result = [
            {"id": "incident_1", "issue_id": "issue_1"},
            {"id": "incident_2", "issue_id": "issue_2"},
        ]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = setup_mock_cursor(mock_connection)

        result = get_issue_first_seen_data(
            issue_id_list=["issue_1", "issue_2", "issue_3"]
        )

        assert result == expected_result
        execute_call = mock_cursor.execute.call_args
        query = execute_call[0][0]
        assert "IN" in query
        mock_set_cache.assert_called_once()

    @patch("kernelCI_app.queries.issues.get_query_cache")
    def test_get_issue_first_seen_data_empty_list(self, mock_get_cache):
        result = get_issue_first_seen_data(issue_id_list=[])

        assert result == []
        mock_get_cache.assert_not_called()


class TestGetIssueTreesData:
    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connections")
    def test_get_issue_trees_data_success(self, mock_connections, mock_dict_fetchall):
        expected_result = [{"issue_id": "issue_1", "issue_version": 1}]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = MagicMock()
        mock_connections.__getitem__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        result = get_issue_trees_data(issue_key_list=[("issue_1", 1), ("issue_2", 2)])

        assert result == expected_result

    def test_get_issue_trees_data_empty_list(self):
        result = get_issue_trees_data(issue_key_list=[])

        assert result == []

    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connections")
    def test_get_issue_trees_data_multiple_issues(
        self, mock_connections, mock_dict_fetchall
    ):
        expected_result = [
            {
                "issue_id": "issue_1",
                "issue_version": 1,
                "checkout_id": "checkout_1",
                "tree_name": "mainline",
                "git_repository_url": "https://my_url.com",
                "git_repository_branch": "master",
                "incident_issue_id": "issue_1",
                "incident_issue_version": 1,
            },
            {
                "issue_id": "issue_2",
                "issue_version": 2,
                "checkout_id": None,
                "tree_name": None,
                "git_repository_url": None,
                "git_repository_branch": None,
                "incident_issue_id": None,
                "incident_issue_version": None,
            },
        ]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = MagicMock()
        mock_connections.__getitem__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        result = get_issue_trees_data(
            issue_key_list=[("issue_1", 1), ("issue_2", 2), ("issue_3", 3)]
        )

        assert result == expected_result
        execute_call = mock_cursor.execute.call_args
        query = execute_call[0][0]
        assert "IN" in query
        assert result[0]["incident_issue_id"] == "issue_1"
        assert result[0]["incident_issue_version"] == 1
        assert result[1]["incident_issue_id"] is None
        assert result[1]["incident_issue_version"] is None

    @patch("kernelCI_app.queries.issues.dict_fetchall")
    @patch("kernelCI_app.queries.issues.connections")
    def test_get_issue_trees_data_issue_with_no_incidents(
        self, mock_connections, mock_dict_fetchall
    ):
        expected_result = [
            {
                "issue_id": "issue_1",
                "issue_version": 1,
                "checkout_id": None,
                "tree_name": None,
                "git_repository_url": None,
                "git_repository_branch": None,
                "incident_issue_id": None,
                "incident_issue_version": None,
            }
        ]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = MagicMock()
        mock_connections.__getitem__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        result = get_issue_trees_data(issue_key_list=[("issue_1", 1)])

        assert result == expected_result
        assert result[0]["incident_issue_id"] is None
        assert result[0]["incident_issue_version"] is None
