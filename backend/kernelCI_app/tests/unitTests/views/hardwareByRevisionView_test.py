from http import HTTPStatus
from unittest.mock import patch

from django.test.testcases import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.views.hardwareByRevisionView import HardwareByRevisionView


class TestHardwareByRevisionView(SimpleTestCase):
    @patch(
        "kernelCI_app.views.hardwareByRevisionView."
        "get_hardware_listing_data_by_revision"
    )
    def test_get_passes_independent_filters(self, mock_get_listing):
        mock_get_listing.return_value = [("platform1", ["hardware1"], *range(9))]
        request = APIRequestFactory().get(
            "/hardware-by-revision/",
            {
                "checkoutOrigin": "checkout-origin",
                "buildOrigin": "build-origin",
                "testOrigin": "test-origin",
                "buildLab": "build-lab",
                "testLab": "test-lab",
                "tree_name": "tree",
                "git_repository_url": "https://example.com/linux.git",
                "git_repository_branch": "main",
                "git_commit_hash": "a" * 40,
            },
        )

        response = HardwareByRevisionView().get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_get_listing.assert_called_once_with(
            checkout_origin=["checkout-origin"],
            build_origin=["build-origin"],
            test_origin=["test-origin"],
            build_lab=["build-lab"],
            test_lab=["test-lab"],
            tree_name="tree",
            git_repository_url="https://example.com/linux.git",
            git_repository_branch="main",
            git_commit_hash="a" * 40,
        )

    @patch(
        "kernelCI_app.views.hardwareByRevisionView."
        "get_hardware_listing_data_by_revision"
    )
    def test_origin_is_deprecated_checkout_and_build_alias(self, mock_get_listing):
        mock_get_listing.return_value = []
        request = APIRequestFactory().get(
            "/hardware-by-revision/",
            {
                "origin": "legacy",
                "tree_name": "tree",
                "git_repository_url": "https://example.com/linux.git",
                "git_repository_branch": "main",
                "git_commit_hash": "a" * 40,
            },
        )

        response = HardwareByRevisionView().get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            mock_get_listing.call_args.kwargs["checkout_origin"], ["legacy"]
        )
        self.assertEqual(mock_get_listing.call_args.kwargs["build_origin"], ["legacy"])
        self.assertIsNone(mock_get_listing.call_args.kwargs["test_origin"])
