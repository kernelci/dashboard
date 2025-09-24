from unittest.mock import patch
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from kernelCI_app.views.buildDetailsView import BuildDetails
from kernelCI_app.tests.unitTests.views.fixtures.build_data import build_details_data


class TestBuildDetails(SimpleTestCase):
    """Test cases for BuildDetails view."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = BuildDetails()
        self.build_id = "test_build_123"
        self.url = f"/builds/{self.build_id}"

    @patch("kernelCI_app.views.buildDetailsView.get_build_details")
    def test_get_build_details_success(self, mock_get_build_details):
        """Test successful build details retrieval."""

        mock_get_build_details.return_value = [build_details_data]

        request = self.factory.get(self.url)
        response = self.view.get(request, build_id=self.build_id)

        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["id"], build_details_data["id"])

    @patch("kernelCI_app.views.buildDetailsView.get_build_details")
    def test_get_build_details_not_found(self, mock_get_build_details):
        """Test build details not found."""
        mock_get_build_details.return_value = []

        request = self.factory.get(self.url)
        response = self.view.get(request, build_id=self.build_id)

        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.data)

    @patch("kernelCI_app.views.buildDetailsView.get_build_details")
    def test_get_build_details_validation_error(self, mock_get_build_details):
        """Test validation error in build details response."""
        mock_get_build_details.return_value = [{"invalid": "data"}]

        request = self.factory.get(self.url)
        response = self.view.get(request, build_id=self.build_id)

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.data)
