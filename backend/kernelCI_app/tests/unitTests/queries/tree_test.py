from unittest.mock import patch

from kernelCI_app.queries.tree import (
    get_latest_tree,
    get_tree_details_data,
)
from kernelCI_app.tests.unitTests.queries.conftest import (
    setup_mock_cursor,
    setup_mock_queryset,
)


class TestGetTreeDetailsData:
    @patch("kernelCI_app.queries.tree.get_query_cache")
    def test_get_tree_details_data_from_cache(self, mock_get_cache):
        cached_data = [("row1", "row2")]
        mock_get_cache.return_value = cached_data

        result = get_tree_details_data(
            origin_param="maestro",
            git_url_param="https://my_url.com",
            git_branch_param="master",
            commit_hash="abc123",
        )

        assert result == cached_data

    @patch("kernelCI_app.queries.tree.get_query_cache")
    @patch("kernelCI_app.queries.tree.set_query_cache")
    @patch("kernelCI_app.queries.tree.create_checkouts_where_clauses")
    @patch("kernelCI_app.queries.tree.connection")
    def test_get_tree_details_data_from_database(
        self,
        mock_connection,
        mock_create_clauses,
        mock_set_cache,
        mock_get_cache,
    ):
        expected_data = [("row1", "row2")]
        mock_get_cache.return_value = None
        mock_create_clauses.return_value = {
            "git_branch_clause": "git_repository_branch = %(git_branch_param)s",
            "tree_name_clause": "",
            "git_url_clause": "git_repository_url = %(git_url_param)s",
        }
        mock_cursor = setup_mock_cursor(mock_connection)
        mock_cursor.fetchall.return_value = expected_data

        result = get_tree_details_data(
            origin_param="maestro",
            git_url_param="https://my_url.com",
            git_branch_param="master",
            commit_hash="abc123",
        )

        assert result == expected_data
        mock_set_cache.assert_called_once()


class TestGetLatestTree:
    @patch("kernelCI_app.queries.tree.Checkouts")
    def test_get_latest_tree_success(self, mock_checkouts_model):
        expected_result = {"git_commit_hash": "abc123", "tree_name": "mainline"}
        setup_mock_queryset(mock_checkouts_model, expected_result)

        result = get_latest_tree(
            tree_name="mainline",
            git_branch="master",
            origin="maestro",
            git_commit_hash="abc123",
        )

        assert result == expected_result

    @patch("kernelCI_app.queries.tree.Checkouts")
    def test_get_latest_tree_not_found(self, mock_checkouts_model):
        setup_mock_queryset(mock_checkouts_model, None)

        result = get_latest_tree(
            tree_name="nonexistent_tree",
            git_branch="master",
            origin="maestro",
            git_commit_hash=None,
        )

        assert result is None

    @patch("kernelCI_app.queries.tree.Checkouts")
    def test_get_latest_tree_not_found_with_commit_hash(self, mock_checkouts_model):
        setup_mock_queryset(mock_checkouts_model, None)

        result = get_latest_tree(
            tree_name="nonexistent_tree",
            git_branch="master",
            origin="maestro",
            git_commit_hash="nonexistent_hash",
        )

        assert result is None
