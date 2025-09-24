from unittest.mock import patch
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from kernelCI_app.views.buildIssuesView import BuildIssuesView
from kernelCI_app.tests.unitTests.views.fixtures.build_data import base_issue_data


class TestBuildIssuesView(SimpleTestCase):
    """Test cases for BuildIssuesView."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = BuildIssuesView()
        self.build_id = "test_build_123"
        self.url = f"/builds/{self.build_id}/issues"

    @patch("kernelCI_app.views.buildIssuesView.sanitize_details_issues_rows")
    @patch("kernelCI_app.views.buildIssuesView.get_build_issues")
    def test_get_build_issues_success(self, mock_get_build_issues, mock_sanitize):
        """Test successful build issues retrieval."""
        mock_get_build_issues.return_value = [{}]
        mock_sanitize.return_value = [base_issue_data]

        request = self.factory.get(self.url)
        response = self.view.get(request, build_id=self.build_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], base_issue_data["id"])

    @patch("kernelCI_app.views.buildIssuesView.sanitize_details_issues_rows")
    @patch("kernelCI_app.views.buildIssuesView.get_build_issues")
    def test_get_build_issues_empty(self, mock_get_build_issues, mock_sanitize):
        """Test build issues not found."""
        mock_get_build_issues.return_value = []
        mock_sanitize.return_value = []

        request = self.factory.get(self.url)
        response = self.view.get(request, build_id=self.build_id)

        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.data)

    @patch("kernelCI_app.views.buildIssuesView.sanitize_details_issues_rows")
    @patch("kernelCI_app.views.buildIssuesView.get_build_issues")
    def test_get_build_issues_validation_error(
        self, mock_get_build_issues, mock_sanitize
    ):
        """Test validation error in build issues response."""
        mock_records = [{"invalid": "data"}]
        mock_sanitize.return_value = [{"invalid": "data"}]
        mock_get_build_issues.return_value = mock_records

        request = self.factory.get(self.url)
        response = self.view.get(request, build_id=self.build_id)

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.data)
