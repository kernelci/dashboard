from unittest.mock import Mock, patch

from kernelCI_app.queries.test import get_test_details_data, get_test_status_history
from kernelCI_app.tests.unitTests.queries.conftest import (
    setup_mock_cursor,
)


class TestGetTestDetailsData:
    @patch("kernelCI_app.queries.test.dict_fetchall")
    @patch("kernelCI_app.queries.test.connection")
    def test_get_test_details_data_success(self, mock_connection, mock_dict_fetchall):
        expected_result = [{"id": "test", "status": "PASS"}]
        mock_dict_fetchall.return_value = expected_result
        mock_cursor = setup_mock_cursor(mock_connection)

        result = get_test_details_data(test_id="test")

        assert result == expected_result
        mock_cursor.execute.assert_called_once()

    @patch("kernelCI_app.queries.test.dict_fetchall")
    @patch("kernelCI_app.queries.test.connection")
    def test_get_test_details_data_empty_result(
        self, mock_connection, mock_dict_fetchall
    ):
        mock_dict_fetchall.return_value = []
        setup_mock_cursor(mock_connection)

        result = get_test_details_data(test_id="test")

        assert result == []


class TestGetTestStatusHistory:
    @patch("kernelCI_app.queries.test.transaction.atomic")
    @patch("kernelCI_app.queries.test.set_query_cache")
    @patch("kernelCI_app.queries.test.get_query_cache")
    @patch("kernelCI_app.queries.test.dict_fetchall")
    @patch("kernelCI_app.queries.test.connection")
    def test_get_test_status_history_with_platform(
        self,
        mock_connection,
        mock_dict_fetchall,
        mock_get_cache,
        mock_set_cache,
        mock_transaction,
    ):
        mock_transaction.return_value.__enter__ = Mock(return_value=None)
        mock_transaction.return_value.__exit__ = Mock(return_value=None)
        expected_result = [{"id": "test", "status": "PASS"}]
        mock_dict_fetchall.return_value = expected_result
        mock_get_cache.return_value = None
        mock_cursor = setup_mock_cursor(mock_connection)

        result = get_test_status_history(
            path="boot",
            origin="maestro",
            git_repository_url="https://my_url.com",
            git_repository_branch="master",
            platform="x86_64",
            test_start_time="2025-11-11T10:00:00Z",
            config_name="defconfig",
            field_timestamp=None,
            group_size=10,
        )

        assert result == expected_result
        assert mock_cursor.execute.call_count > 1
        query_call = mock_cursor.execute.call_args_list[1]
        assert "platform" in query_call[0][1]
        assert query_call[0][1]["platform"] == "x86_64"
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_called_once()
        mock_transaction.assert_called_once()

    @patch("kernelCI_app.queries.test.transaction.atomic")
    @patch("kernelCI_app.queries.test.set_query_cache")
    @patch("kernelCI_app.queries.test.get_query_cache")
    @patch("kernelCI_app.queries.test.dict_fetchall")
    @patch("kernelCI_app.queries.test.connection")
    def test_get_test_status_history_without_platform(
        self,
        mock_connection,
        mock_dict_fetchall,
        mock_get_cache,
        mock_set_cache,
        mock_transaction,
    ):
        mock_transaction.return_value.__enter__ = Mock(return_value=None)
        mock_transaction.return_value.__exit__ = Mock(return_value=None)
        expected_result = []
        mock_dict_fetchall.return_value = expected_result
        mock_get_cache.return_value = None
        mock_cursor = setup_mock_cursor(mock_connection)

        result = get_test_status_history(
            path="boot",
            origin="maestro",
            git_repository_url="https://my_url.com",
            git_repository_branch="master",
            platform=None,
            test_start_time=None,
            config_name="defconfig",
            field_timestamp="2025-11-11T10:00:00Z",
            group_size=10,
        )

        assert result == expected_result
        query_call = mock_cursor.execute.call_args_list[1]
        assert "field_timestamp" in query_call[0][1]
        assert query_call[0][1]["field_timestamp"] == "2025-11-11T10:00:00Z"
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_called_once()
        mock_transaction.assert_called_once()

    @patch("kernelCI_app.queries.test.transaction.atomic")
    @patch("kernelCI_app.queries.test.set_query_cache")
    @patch("kernelCI_app.queries.test.get_query_cache")
    @patch("kernelCI_app.queries.test.dict_fetchall")
    @patch("kernelCI_app.queries.test.connection")
    def test_get_test_status_history_uses_start_time_when_provided(
        self,
        mock_connection,
        mock_dict_fetchall,
        mock_get_cache,
        mock_set_cache,
        mock_transaction,
    ):
        mock_transaction.return_value.__enter__ = Mock(return_value=None)
        mock_transaction.return_value.__exit__ = Mock(return_value=None)
        mock_dict_fetchall.return_value = []
        mock_get_cache.return_value = None
        mock_cursor = setup_mock_cursor(mock_connection)

        get_test_status_history(
            path="boot",
            origin="maestro",
            git_repository_url="https://my_url.com",
            git_repository_branch="master",
            platform="x86_64",
            test_start_time="2025-11-10T10:00:00Z",
            config_name="defconfig",
            field_timestamp=None,
            group_size=10,
        )

        query_call = mock_cursor.execute.call_args_list[1]
        assert "test_start_time" in query_call[0][1]
        assert query_call[0][1]["test_start_time"] == "2025-11-10T10:00:00Z"
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_called_once()
        mock_transaction.assert_called_once()

    @patch("kernelCI_app.queries.test.transaction.atomic")
    @patch("kernelCI_app.queries.test.set_query_cache")
    @patch("kernelCI_app.queries.test.get_query_cache")
    @patch("kernelCI_app.queries.test.dict_fetchall")
    @patch("kernelCI_app.queries.test.connection")
    def test_get_test_status_history_with_null_timestamps(
        self,
        mock_connection,
        mock_dict_fetchall,
        mock_get_cache,
        mock_set_cache,
        mock_transaction,
    ):
        mock_transaction.return_value.__enter__ = Mock(return_value=None)
        mock_transaction.return_value.__exit__ = Mock(return_value=None)
        expected_result = []
        mock_dict_fetchall.return_value = expected_result
        mock_get_cache.return_value = None
        mock_cursor = setup_mock_cursor(mock_connection)

        result = get_test_status_history(
            path="boot",
            origin="maestro",
            git_repository_url="https://my_url.com",
            git_repository_branch="master",
            platform=None,
            test_start_time=None,
            config_name="defconfig",
            field_timestamp=None,
            group_size=10,
        )

        assert result == expected_result
        query_call = mock_cursor.execute.call_args_list[1]
        sql = query_call[0][0]
        assert "T.START_TIME IS NULL" in sql
        assert "T._TIMESTAMP IS NULL" in sql
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_called_once()
        mock_transaction.assert_called_once()

    @patch("kernelCI_app.queries.test.set_query_cache")
    @patch("kernelCI_app.queries.test.get_query_cache")
    @patch("kernelCI_app.queries.test.dict_fetchall")
    def test_get_test_status_history_returns_cached_result(
        self,
        mock_dict_fetchall,
        mock_get_cache,
        mock_set_cache,
    ):
        cached_result = [{"id": "cached", "status": "PASS"}]
        mock_get_cache.return_value = cached_result

        result = get_test_status_history(
            path="boot",
            origin="maestro",
            git_repository_url="https://my_url.com",
            git_repository_branch="master",
            platform="x86_64",
            test_start_time="2025-11-11T10:00:00Z",
            config_name="defconfig",
            field_timestamp=None,
            group_size=10,
        )

        assert result == cached_result
        mock_dict_fetchall.assert_not_called()
        mock_set_cache.assert_not_called()
        mock_get_cache.assert_called_once()
