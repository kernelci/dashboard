from unittest.mock import MagicMock
from kernelCI_app.helpers.database import dict_fetchall


class TestDictFetchall:
    def test_dict_fetchall_with_data(self):
        """Test dict_fetchall with sample data."""
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",), ("status",)]
        mock_cursor.fetchall.return_value = [
            (1, "test1", "PASS"),
            (2, "test2", "FAIL"),
            (3, "test3", "SKIP"),
        ]

        result = dict_fetchall(mock_cursor)

        expected = [
            {"id": 1, "name": "test1", "status": "PASS"},
            {"id": 2, "name": "test2", "status": "FAIL"},
            {"id": 3, "name": "test3", "status": "SKIP"},
        ]
        assert result == expected

    def test_dict_fetchall_with_empty_data(self):
        """Test dict_fetchall with empty result set."""
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",)]
        mock_cursor.fetchall.return_value = []

        result = dict_fetchall(mock_cursor)

        assert result == []

    def test_dict_fetchall_with_single_column(self):
        """Test dict_fetchall with single column."""
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",)]
        mock_cursor.fetchall.return_value = [(1,), (2,), (3,)]

        result = dict_fetchall(mock_cursor)

        expected = [{"id": 1}, {"id": 2}, {"id": 3}]
        assert result == expected
