from unittest.mock import patch

from kernelCI_app.queries.labs import get_lab_origins
from kernelCI_app.tests.unitTests.queries.conftest import setup_mock_cursor


class TestGetLabOrigins:
    @patch("kernelCI_app.queries.labs.get_query_cache")
    def test_get_lab_origins_from_cache(self, mock_get_cache):
        cached_data = ["maestro", "redhat"]
        mock_get_cache.return_value = cached_data

        result = get_lab_origins(interval_in_days=7)

        assert result == cached_data

    @patch("kernelCI_app.queries.labs.get_query_cache")
    @patch("kernelCI_app.queries.labs.set_query_cache")
    @patch("kernelCI_app.queries.labs.connection")
    def test_get_lab_origins_from_database(
        self, mock_connection, mock_set_cache, mock_get_cache
    ):
        mock_get_cache.return_value = None
        mock_cursor = setup_mock_cursor(mock_connection)
        mock_cursor.fetchall.return_value = [("maestro",), ("redhat",)]

        result = get_lab_origins(interval_in_days=7)

        assert result == ["maestro", "redhat"]
        mock_cursor.execute.assert_called_once()
        mock_set_cache.assert_called_once()

    @patch("kernelCI_app.queries.labs.get_query_cache")
    @patch("kernelCI_app.queries.labs.set_query_cache")
    @patch("kernelCI_app.queries.labs.connection")
    def test_get_lab_origins_empty_result_does_not_cache(
        self, mock_connection, mock_set_cache, mock_get_cache
    ):
        mock_get_cache.return_value = None
        mock_cursor = setup_mock_cursor(mock_connection)
        mock_cursor.fetchall.return_value = []

        result = get_lab_origins(interval_in_days=7)

        assert result == []
        mock_set_cache.assert_not_called()
