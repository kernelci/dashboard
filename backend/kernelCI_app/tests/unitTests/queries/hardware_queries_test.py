from datetime import datetime
from unittest.mock import patch

from kernelCI_app.queries.hardware import (
    get_hardware_listing_data,
    get_hardware_details_data,
    get_hardware_trees_data,
    get_hardware_commit_history,
    _generate_query_params,
    query_records,
)
from kernelCI_app.typeModels.hardwareDetails import CommitHead

from kernelCI_app.tests.unitTests.queries.conftest import (
    TEST_TREE,
    setup_mock_cursor,
)

START_DATE = datetime(2025, 11, 11)
END_DATE = datetime(2025, 11, 12)


class TestGetHardwareListingData:
    @patch("kernelCI_app.queries.hardware.connection")
    def test_get_hardware_listing_data_success(self, mock_connection):
        expected_result = [
            ("platform", ["compatible"], 10, 5, 0, 0, 0, 0, 0, 20, 10, 0, 0, 0, 0, 0)
        ]
        mock_cursor = setup_mock_cursor(mock_connection)
        mock_cursor.fetchall.return_value = expected_result

        result = get_hardware_listing_data(
            start_date=datetime(2025, 11, 10),
            end_date=datetime(2025, 11, 12),
            origin="maestro",
        )

        assert result == expected_result
        mock_cursor.execute.assert_called_once()


class TestGetHardwareDetailsData:
    @patch("kernelCI_app.queries.hardware.get_query_cache")
    def test_get_hardware_details_data_from_cache(self, mock_get_cache):
        cached_data = [{"id": "test", "status": "PASS"}]
        mock_get_cache.return_value = cached_data

        result = get_hardware_details_data(
            hardware_id="hardware",
            origin="maestro",
            trees_with_selected_commits=[TEST_TREE],
            start_datetime=START_DATE,
            end_datetime=END_DATE,
        )

        assert result == cached_data

    @patch("kernelCI_app.queries.hardware.get_query_cache")
    @patch("kernelCI_app.queries.hardware.set_query_cache")
    @patch("kernelCI_app.queries.hardware.query_records")
    def test_get_hardware_details_data_from_database(
        self, mock_query_records, mock_set_cache, mock_get_cache
    ):
        expected_data = [{"id": "test", "status": "PASS"}]
        mock_get_cache.return_value = None
        mock_query_records.return_value = expected_data

        result = get_hardware_details_data(
            hardware_id="hardware",
            origin="maestro",
            trees_with_selected_commits=[TEST_TREE],
            start_datetime=START_DATE,
            end_datetime=END_DATE,
        )

        assert result == expected_data
        mock_query_records.assert_called_once()
        mock_set_cache.assert_called_once()


class TestGetHardwareTreesData:
    @patch("kernelCI_app.queries.hardware.get_query_cache")
    def test_get_hardware_trees_data_from_cache(self, mock_get_cache):
        cached_trees = [TEST_TREE]
        mock_get_cache.return_value = cached_trees

        result = get_hardware_trees_data(
            hardware_id="hardware",
            origin="maestro",
            start_datetime=START_DATE,
            end_datetime=END_DATE,
        )

        assert result == cached_trees

    @patch("kernelCI_app.queries.hardware.get_query_cache")
    @patch("kernelCI_app.queries.hardware.set_query_cache")
    @patch("kernelCI_app.queries.hardware.dict_fetchall")
    @patch("kernelCI_app.queries.hardware.connection")
    def test_get_hardware_trees_data_from_database(
        self, mock_connection, mock_dict_fetchall, mock_set_cache, mock_get_cache
    ):
        tree_records = [
            {
                "tree_name": "mainline",
                "origin": "maestro",
                "git_repository_branch": "master",
                "git_repository_url": "https://my_url.com",
                "git_commit_name": "v6.1",
                "git_commit_hash": "abc123",
                "git_commit_tags": None,
            }
        ]
        mock_get_cache.return_value = None
        mock_dict_fetchall.return_value = tree_records
        setup_mock_cursor(mock_connection)

        result = get_hardware_trees_data(
            hardware_id="hardware",
            origin="maestro",
            start_datetime=START_DATE,
            end_datetime=END_DATE,
        )

        assert len(result) == 1
        assert result[0].tree_name == "mainline"
        mock_set_cache.assert_called_once()


class TestGenerateQueryParams:
    def test_generate_query_params_single_commit(self):
        commit_heads = [
            CommitHead(
                treeName="mainline",
                repositoryUrl="https://my_url.com",
                branch="master",
                commitHash="abc123",
            )
        ]

        result = _generate_query_params(commit_heads)

        assert "tuple_str" in result
        assert "query_params" in result
        assert result["query_params"]["tree_name0"] == "mainline"
        assert result["query_params"]["git_commit_hash0"] == "abc123"

    def test_generate_query_params_multiple_commits(self):
        commit_heads = [
            CommitHead(
                treeName="mainline",
                repositoryUrl="https://my_url.com",
                branch="master",
                commitHash="abc123",
            ),
            CommitHead(
                treeName="next",
                repositoryUrl="https://my_url.com",
                branch="master",
                commitHash="def456",
            ),
        ]

        result = _generate_query_params(commit_heads)

        assert len(result["query_params"]) == 8
        assert "tree_name0" in result["query_params"]
        assert "tree_name1" in result["query_params"]


class TestGetHardwareCommitHistory:
    @patch("kernelCI_app.queries.hardware.connection")
    def test_get_hardware_commit_history_success(self, mock_connection):
        expected_result = [("abc123", "v6.1", None, datetime(2025, 11, 12))]
        mock_cursor = setup_mock_cursor(mock_connection)
        mock_cursor.fetchall.return_value = expected_result

        result = get_hardware_commit_history(
            origin="maestro",
            start_date=datetime(2025, 11, 11),
            end_date=datetime(2025, 11, 12),
            commit_heads=[
                CommitHead(
                    treeName="mainline",
                    repositoryUrl="https://my_url.com",
                    branch="master",
                    commitHash="abc123",
                )
            ],
        )

        assert result == expected_result

    @patch("kernelCI_app.queries.hardware.connection")
    def test_get_hardware_commit_history_empty_commits(self, mock_connection):
        result = get_hardware_commit_history(
            origin="maestro",
            start_date=datetime(2025, 11, 11),
            end_date=datetime(2025, 11, 12),
            commit_heads=[],
        )

        assert result is None
        mock_connection.cursor.assert_not_called()


class TestQueryRecords:
    @patch("kernelCI_app.queries.hardware.dict_fetchall")
    @patch("kernelCI_app.queries.hardware.connection")
    def test_query_records_success(self, mock_connection, mock_dict_fetchall):
        expected_result = [{"id": "test", "status": "PASS"}]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = setup_mock_cursor(mock_connection)

        result = query_records(
            hardware_id="hardware",
            origin="maestro",
            trees=[TEST_TREE],
            start_date=START_DATE,
            end_date=END_DATE,
        )

        assert result == expected_result
        mock_cursor.execute.assert_called_once()
