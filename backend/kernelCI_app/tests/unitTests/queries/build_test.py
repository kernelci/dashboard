from unittest.mock import patch

from kernelCI_app.queries.build import get_build_details, get_build_tests
from kernelCI_app.tests.unitTests.queries.conftest import (
    setup_mock_filter_values_queryset,
    setup_mock_query_builder,
)


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
    @patch("kernelCI_app.queries.build.Tests")
    def test_get_build_tests_success(self, mock_tests_model):
        setup_mock_filter_values_queryset(
            mock_tests_model,
            [
                {
                    "id": "test",
                    "duration": 30,
                    "status": "PASS",
                    "path": "test.path",
                    "start_time": "2024-01-15T10:00:00Z",
                    "environment_compatible": ["hardware1"],
                    "environment_misc": {"platform": "x86_64"},
                    "build__status": "PASS",
                    "lab_name": "lab-a",
                }
            ],
        )

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
        mock_tests_model.objects.filter.assert_called_once_with(build_id="build")

    @patch("kernelCI_app.queries.build.Tests")
    def test_get_build_tests_empty_result(self, mock_tests_model):
        setup_mock_filter_values_queryset(mock_tests_model, [])

        result = get_build_tests("build")

        assert result == []
