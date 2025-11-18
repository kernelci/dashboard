from unittest.mock import Mock, patch

from kernelCI_app.queries.tree import (
    get_tree_listing_data,
    get_tree_listing_fast,
    get_tree_listing_data_by_checkout_id,
    get_tree_details_data,
    get_tree_commit_history,
    get_latest_tree,
)

from kernelCI_app.tests.unitTests.queries.conftest import (
    setup_mock_cursor,
    setup_mock_queryset,
)


class TestGetTreeListingData:
    @patch("kernelCI_app.queries.tree.dict_fetchall")
    @patch("kernelCI_app.queries.tree.connection")
    def test_get_tree_listing_data_success(self, mock_connection, mock_dict_fetchall):
        expected_result = [{"checkout_id": "checkout", "tree_name": "mainline"}]
        mock_dict_fetchall.return_value = expected_result
        setup_mock_cursor(mock_connection)

        result = get_tree_listing_data(origin="maestro", interval_in_days=7)

        assert result == expected_result


class TestGetTreeListingFast:
    @patch("kernelCI_app.queries.tree.get_query_time_interval")
    @patch("kernelCI_app.queries.tree.Checkouts")
    def test_get_tree_listing_fast_with_origin(
        self, mock_checkouts_model, mock_get_interval
    ):
        mock_get_interval.return_value.timestamp.return_value = 1704067200.0
        mock_checkouts_model.objects.raw.return_value = [Mock(id="checkout")]

        result = get_tree_listing_fast(origin="maestro", interval={"days": 7})

        assert len(result) == 1

    @patch("kernelCI_app.queries.tree.get_query_time_interval")
    @patch("kernelCI_app.queries.tree.Checkouts")
    def test_get_tree_listing_fast_without_origin(
        self, mock_checkouts_model, mock_get_interval
    ):
        mock_get_interval.return_value.timestamp.return_value = 1704067200.0
        mock_checkouts_model.objects.raw.return_value = []

        result = get_tree_listing_fast(origin=None, interval={"days": 7})

        assert result == []


class TestGetTreeListingDataByCheckoutId:
    @patch("kernelCI_app.queries.tree.dict_fetchall")
    @patch("kernelCI_app.queries.tree.connection")
    def test_get_tree_listing_data_by_checkout_id_success(
        self, mock_connection, mock_dict_fetchall
    ):
        expected_result = [{"id": "checkout_1", "tree_name": "mainline"}]
        mock_dict_fetchall.return_value = expected_result
        setup_mock_cursor(mock_connection)

        result = get_tree_listing_data_by_checkout_id(
            checkout_ids=["checkout_1", "checkout_2"]
        )

        assert result == expected_result


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


class TestGetTreeCommitHistory:
    @patch("kernelCI_app.queries.tree.create_checkouts_where_clauses")
    @patch("kernelCI_app.queries.tree.connection")
    def test_get_tree_commit_history_success(
        self, mock_connection, mock_create_clauses
    ):
        expected_result = [("abc123", "v6.1", None, "2025-11-10T10:00:00Z")]
        mock_create_clauses.return_value = {
            "git_branch_clause": "git_repository_branch = %(git_branch_param)s",
            "tree_name_clause": "tree_name = %(tree_name)s",
            "git_url_clause": "git_repository_url = %(git_url_param)s",
        }
        mock_cursor = setup_mock_cursor(mock_connection)
        mock_cursor.fetchall.return_value = expected_result

        result = get_tree_commit_history(
            commit_hash="abc123",
            origin="maestro",
            git_url="https://my_url.com",
            git_branch="master",
            tree_name="mainline",
        )

        assert result == expected_result
        mock_create_clauses.assert_called_once_with(
            git_url="https://my_url.com", git_branch="master", tree_name="mainline"
        )


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
