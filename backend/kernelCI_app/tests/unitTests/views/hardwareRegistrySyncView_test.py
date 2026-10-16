from datetime import datetime, timezone
from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from kernelCI_app.views.hardwareRegistrySyncView import HardwareRegistrySyncView


class TestHardwareRegistrySyncView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = HardwareRegistrySyncView()

    @patch("kernelCI_app.views.hardwareRegistrySyncView.HardwareRegistrySync.objects")
    def test_no_row_returns_empty_sync(self, objects):
        objects.filter.return_value.first.return_value = None

        response = self.view.get(self.factory.get("/hardware/registry-sync/"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, {"synced_at": None, "files": []})

    @patch("kernelCI_app.views.hardwareRegistrySyncView.HardwareRegistrySync.objects")
    def test_row_returns_each_file(self, objects):
        objects.filter.return_value.first.return_value = SimpleNamespace(
            synced_at=datetime(2026, 6, 24, 3, 0, tzinfo=timezone.utc),
            files=[
                {
                    "name": "index.yaml",
                    "url": "https://example/index.yaml",
                    "content_hash": "a" * 64,
                },
                {
                    "name": "ti.yaml",
                    "url": "https://example/ti.yaml",
                    "content_hash": "b" * 64,
                },
            ],
        )

        response = self.view.get(self.factory.get("/hardware/registry-sync/"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["synced_at"], "2026-06-24T03:00:00Z")
        self.assertEqual(
            [item["name"] for item in response.data["files"]],
            ["index.yaml", "ti.yaml"],
        )
        self.assertNotEqual(
            response.data["files"][0]["content_hash"],
            response.data["files"][1]["content_hash"],
        )
