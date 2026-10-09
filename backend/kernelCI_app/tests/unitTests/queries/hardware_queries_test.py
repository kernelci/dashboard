from datetime import datetime
from unittest.mock import patch

from kernelCI_app.queries.hardware import (
    _generate_query_params,
    get_hardware_commit_history,
    get_hardware_details_data,
    get_hardware_details_summary,
    get_hardware_trees_data,
    query_records,
)
from kernelCI_app.tests.unitTests.queries.conftest import (
    TEST_TREE,
    setup_mock_cursor,
)
from kernelCI_app.typeModels.hardwareDetails import CommitHead

START_DATE = datetime(2025, 11, 11)
END_DATE = datetime(2025, 11, 12)


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
    @patch("kernelCI_app.queries.hardware.connections")
    def test_get_hardware_trees_data_from_database(
        self, mock_connections, mock_dict_fetchall, mock_set_cache, mock_get_cache
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
        setup_mock_cursor(mock_connections.__getitem__.return_value)

        result = get_hardware_trees_data(
            hardware_id="hardware",
            origin="maestro",
            start_datetime=START_DATE,
            end_datetime=END_DATE,
        )

        assert len(result) == 1
        assert result[0].tree_name == "mainline"
        mock_set_cache.assert_called_once()
        mock_connections.__getitem__.assert_called_with("default")


class TestGetHardwareDetailsSummary:
    @patch("kernelCI_app.queries.hardware.get_query_cache", return_value=None)
    @patch("kernelCI_app.queries.hardware.set_query_cache")
    @patch("kernelCI_app.queries.hardware.dict_fetchall", return_value=[])
    @patch("kernelCI_app.queries.hardware.connection")
    def test_filters_by_checkout_identity(
        self, mock_connection, mock_dict_fetchall, mock_set_cache, mock_get_cache
    ):
        mock_cursor = setup_mock_cursor(mock_connection)

        get_hardware_details_summary(
            hardware_id="hardware",
            origin="maestro",
            checkouts=[
                ("mainline", "https://git.kernel.org", "master", "abc123", "maestro"),
                ("mainline", "https://git.kernel.org", "for-next", "abc123", "broonie"),
            ],
            start_datetime=START_DATE,
            end_datetime=END_DATE,
        )

        executed_query, params = mock_cursor.execute.call_args[0]

        assert "checkouts.tree_name" in executed_query
        assert "checkouts.git_repository_branch" in executed_query
        assert "checkouts.git_commit_hash" in executed_query
        assert "checkouts.origin" in executed_query
        assert "ANY(%(commits)s)" not in executed_query
        assert params["tree_name0"] == "mainline"
        assert params["git_repository_branch0"] == "master"
        assert params["commit_hash0"] == "abc123"
        assert params["checkout_origin0"] == "maestro"
        assert params["git_repository_branch1"] == "for-next"
        assert params["checkout_origin1"] == "broonie"

    @patch("kernelCI_app.queries.hardware.connection")
    def test_skips_query_without_checkouts(self, mock_connection):
        result = get_hardware_details_summary(
            hardware_id="hardware",
            origin="maestro",
            checkouts=[],
            start_datetime=START_DATE,
            end_datetime=END_DATE,
        )

        assert result == []
        mock_connection.cursor.assert_not_called()


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

        result = _generate_query_params(commit_heads, default_origin="maestro")

        assert "tuple_str" in result
        assert "query_params" in result
        assert result["query_params"]["tree_name0"] == "mainline"
        assert result["query_params"]["git_commit_hash0"] == "abc123"
        assert result["query_params"]["checkout_origin0"] == "maestro"

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

        result = _generate_query_params(commit_heads, default_origin="maestro")

        assert len(result["query_params"]) == 10
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
                    origin="broonie",
                )
            ],
        )

        assert result == expected_result
        executed_query, params = mock_cursor.execute.call_args[0]
        assert "c.origin = fc.origin" in executed_query
        assert "c.origin = %(origin)s" not in executed_query
        assert params["checkout_origin0"] == "broonie"

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
        executed_query, params = mock_cursor.execute.call_args[0]
        assert "checkouts.tree_name" in executed_query
        assert "checkouts.git_commit_hash" in executed_query
        assert "git_commit_hash IN" not in executed_query
        assert params[-5:] == [
            "mainline",
            "https://my_url.com",
            "master",
            "abc123",
            "maestro",
        ]
