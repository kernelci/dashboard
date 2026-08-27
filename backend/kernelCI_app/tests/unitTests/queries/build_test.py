from unittest.mock import patch

from kernelCI_app.queries.build import get_build_details, get_build_tests
from kernelCI_app.tests.unitTests.queries.conftest import setup_mock_query_builder


class TestGetBuildDetails:
    @patch("kernelCI_app.queries.build.Query")
    def test_get_build_details_success(self, mock_query_class):
        expected_result = [{"id": "build", "checkout_id": "checkout"}]
        mock_query = setup_mock_query_builder(mock_query_class, expected_result)

        result = get_build_details("build")

        assert result == expected_result
        mock_query.where.assert_called_once_with(**{"builds.id__eq": "build"})

    @patch("kernelCI_app.queries.build.Query")
    def test_get_build_details_empty_result(self, mock_query_class):
        setup_mock_query_builder(mock_query_class, [])

        result = get_build_details("build")

        assert result == []


class TestGetBuildTests:
    @patch("kernelCI_app.queries.build.connections")
    def test_get_build_tests_success(self, mock_connections):
        mock_cursor = mock_connections.__getitem__.return_value.cursor.return_value.__enter__.return_value
        mock_cursor.fetchall.return_value = [
            (
                "test",
                30,
                "PASS",
                "test.path",
                "2024-01-15T10:00:00Z",
                ["hardware1"],
                {"platform": "x86_64"},
                "PASS",
                "lab-a",
            )
        ]
        mock_cursor.description = [
            ("id",),
            ("duration",),
            ("status",),
            ("path",),
            ("start_time",),
            ("environment_compatible",),
            ("environment_misc",),
            ("build__status",),
            ("lab",),
        ]

        result = get_build_tests("build")

        assert result == [
            {
                "id": "test",
                "duration": 30,
                "status": "PASS",
                "path": "test.path",
                "start_time": "2024-01-15T10:00:00Z",
                "environment_compatible": ["hardware1"],
                "environment_misc": {"platform": "x86_64"},
                "build__status": "PASS",
                "lab": "lab-a",
            }
        ]
        mock_cursor.execute.assert_called_once()

    @patch("kernelCI_app.queries.build.connections")
    def test_get_build_tests_empty_result(self, mock_connections):
        mock_cursor = mock_connections.__getitem__.return_value.cursor.return_value.__enter__.return_value
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = []

        result = get_build_tests("build")

        assert result == []
