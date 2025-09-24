from unittest.mock import patch
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from kernelCI_app.views.buildTestsView import BuildTests
from kernelCI_app.tests.unitTests.views.fixtures.build_data import (
    base_test_data,
)


class TestBuildTests(SimpleTestCase):
    """Test cases for BuildTests view."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = BuildTests()
        self.build_id = "test_build_123"
        self.url = f"/builds/{self.build_id}/tests"

    @patch("kernelCI_app.views.buildTestsView.get_build_tests")
    def test_get_build_tests_success(self, mock_get_build_tests):
        """Test successful build tests retrieval."""
        mock_get_build_tests.return_value = [base_test_data]

        request = self.factory.get(self.url)
        response = self.view.get(request, build_id=self.build_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], base_test_data["id"])

    @patch("kernelCI_app.views.buildTestsView.get_build_tests")
    def test_get_build_tests_not_found(self, mock_get_build_tests):
        """Test build tests not found."""
        mock_get_build_tests.return_value = None

        request = self.factory.get(self.url)
        response = self.view.get(request, build_id=self.build_id)

        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.data)

    @patch("kernelCI_app.views.buildTestsView.send_discord_notification")
    @patch("kernelCI_app.views.buildTestsView.create_endpoint_notification")
    @patch("kernelCI_app.views.buildTestsView.get_build_tests")
    def test_get_build_tests_failed_build(
        self, mock_get_build_tests, mock_create_notification, mock_send_discord
    ):
        """Test build tests with failed build status."""
        failed_build_data = [
            {**base_test_data, "build__status": "FAIL"},
        ]
        mock_get_build_tests.return_value = failed_build_data
        mock_create_notification.return_value = "Test notification"

        request = self.factory.get(self.url)
        response = self.view.get(request, build_id=self.build_id)

        self.assertEqual(response.status_code, 200)
        mock_create_notification.assert_called_once()
        mock_send_discord.assert_called_once()
        self.assertEqual(response.data[0]["id"], failed_build_data[0]["id"])

    @patch("kernelCI_app.views.buildTestsView.get_build_tests")
    def test_get_build_tests_validation_error(self, mock_get_build_tests):
        """Test validation error in build tests response."""
        mock_get_build_tests.return_value = [{"invalid": "data"}]

        request = self.factory.get(self.url)
        response = self.view.get(request, build_id=self.build_id)

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.data)
