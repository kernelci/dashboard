from unittest.mock import patch

from kernelCI_app.queries.labs import get_lab_listing_data
from kernelCI_app.tests.unitTests.queries.conftest import setup_mock_cursor


class TestGetLabListingData:
    @patch("kernelCI_app.queries.labs.get_query_cache")
    @patch("kernelCI_app.queries.labs.connection")
    def test_get_lab_listing_from_cache(self, mock_connection, mock_get_cache):
        cached = [("lava", 1, 0, 0, 0, 0, 0, 0, 0, 0)]
        mock_get_cache.return_value = cached

        result = get_lab_listing_data(interval_in_days=5)

        assert result == cached
        mock_connection.cursor.assert_not_called()

    @patch("kernelCI_app.queries.labs.get_query_cache")
    @patch("kernelCI_app.queries.labs.set_query_cache")
    @patch("kernelCI_app.queries.labs.connection")
    def test_get_lab_listing_from_database(
        self, mock_connection, mock_set_cache, mock_get_cache
    ):
        rows = [("lava", 1, 0, 0, 0, 0, 0, 0, 0, 0)]
        mock_get_cache.return_value = None
        mock_cursor = setup_mock_cursor(mock_connection)
        mock_cursor.fetchall.return_value = rows

        result = get_lab_listing_data(interval_in_days=5)

        assert result == rows
        assert mock_cursor.execute.call_args[0][1] == {"interval_in_days": 5}
        mock_set_cache.assert_called_once_with(
            key="labListing",
            params={"interval_in_days": 5},
            rows=rows,
        )
