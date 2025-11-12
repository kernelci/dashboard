from unittest.mock import patch

from kernelCI_app.queries.checkout import get_origins

from kernelCI_app.tests.unitTests.queries.conftest import setup_mock_cursor


class TestGetOrigins:
    @patch("kernelCI_app.queries.checkout.get_query_cache")
    def test_get_origins_from_cache(self, mock_get_cache):
        cached_data = [{"origin": "maestro", "table": "checkouts"}]
        mock_get_cache.return_value = cached_data

        result = get_origins(7)

        assert result == cached_data

    @patch("kernelCI_app.queries.checkout.get_query_cache")
    @patch("kernelCI_app.queries.checkout.set_query_cache")
    @patch("kernelCI_app.queries.checkout.dict_fetchall")
    @patch("kernelCI_app.queries.checkout.connection")
    def test_get_origins_from_database(
        self, mock_connection, mock_dict_fetchall, mock_set_cache, mock_get_cache
    ):
        mock_get_cache.return_value = None
        expected_result = [{"origin": "maestro", "table": "checkouts"}]
        mock_dict_fetchall.return_value = expected_result

        mock_cursor = setup_mock_cursor(mock_connection)

        result = get_origins(7)

        assert result == expected_result
        mock_cursor.execute.assert_called_once()
        mock_set_cache.assert_called_once()

    @patch("kernelCI_app.queries.checkout.get_query_cache")
    @patch("kernelCI_app.queries.checkout.set_query_cache")
    @patch("kernelCI_app.queries.checkout.dict_fetchall")
    @patch("kernelCI_app.queries.checkout.connection")
    def test_get_origins_empty_result_does_not_cache(
        self, mock_connection, mock_dict_fetchall, mock_set_cache, mock_get_cache
    ):
        mock_get_cache.return_value = None
        mock_dict_fetchall.return_value = []

        setup_mock_cursor(mock_connection)

        result = get_origins(7)

        assert result == []
        mock_set_cache.assert_not_called()
