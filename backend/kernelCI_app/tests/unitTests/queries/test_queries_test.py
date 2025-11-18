from unittest.mock import patch

from kernelCI_app.queries.test import get_test_details_data, get_test_status_history

from kernelCI_app.tests.unitTests.queries.conftest import (
    setup_mock_cursor,
    setup_mock_test_queryset,
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
    @patch("kernelCI_app.queries.test.Tests")
    def test_get_test_status_history_with_platform(self, mock_tests_model):
        mock_queryset = setup_mock_test_queryset(mock_tests_model)

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

        assert list(result) == []
        mock_queryset.filter.assert_called()

    @patch("kernelCI_app.queries.test.Tests")
    def test_get_test_status_history_without_platform(self, mock_tests_model):
        setup_mock_test_queryset(mock_tests_model)

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

        assert list(result) == []

    @patch("kernelCI_app.queries.test.Tests")
    def test_get_test_status_history_uses_start_time_when_provided(
        self, mock_tests_model
    ):
        mock_queryset = setup_mock_test_queryset(mock_tests_model)

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

        mock_queryset.order_by.assert_called_with("-start_time")

    @patch("kernelCI_app.queries.test.Tests")
    def test_get_test_status_history_with_null_timestamps(self, mock_tests_model):
        mock_queryset = setup_mock_test_queryset(mock_tests_model)

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

        assert list(result) == []
        filter_calls = [str(call) for call in mock_queryset.filter.call_args_list]
        assert any("start_time__isnull" in call for call in filter_calls)
        assert any("field_timestamp__isnull" in call for call in filter_calls)
