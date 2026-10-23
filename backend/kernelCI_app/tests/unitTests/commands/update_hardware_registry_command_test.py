from datetime import datetime, timezone

from django.test import SimpleTestCase

from kernelCI_app.management.commands.update_hardware_registry import (
    apply_updated_at,
    model_kwargs,
    sync_file_entry,
    unwrap_registry,
)
from kernelCI_app.models import HardwareRegistryPlatform


class TestHardwareRegistryParsing(SimpleTestCase):
    def test_two_files_stay_two_entries(self):
        index = sync_file_entry(
            "https://example/hardware_registry/index.yaml",
            b"index",
        )
        vendor = sync_file_entry(
            "https://example/hardware_registry/ti.yaml",
            b"ti",
        )

        self.assertEqual(
            [index["name"], vendor["name"]],
            ["index.yaml", "ti.yaml"],
        )

    def test_unwraps_nested_hardware_registry_and_keeps_flat_files(self):
        nested = unwrap_registry(
            {"hardware_registry": {"registries": ["ti.yaml"], "platforms": {}}}
        )
        flat = unwrap_registry({"registries": ["ti.yaml"], "platforms": {}})

        self.assertEqual(nested["registries"], ["ti.yaml"])
        self.assertEqual(flat, {"registries": ["ti.yaml"], "platforms": {}})

    def test_model_kwargs_keeps_compatible_and_drops_unknown_fields(self):
        kwargs = model_kwargs(
            HardwareRegistryPlatform,
            {
                "id": "board",
                "type": "evaluation_board",
                "vendor_id": "ti",
                "processor_id": "am3358",
                "compatible": ["ti,am335x-bone", "ti,am33xx"],
                "memory_mb": 512,
            },
        )
        self.assertEqual(
            kwargs,
            {
                "id": "board",
                "type": "evaluation_board",
                "vendor_id": "ti",
                "processor_id": "am3358",
                "compatible": ["ti,am335x-bone", "ti,am33xx"],
            },
        )

    def test_unchanged_file_keeps_its_updated_at(self):
        now = datetime(2026, 10, 15, tzinfo=timezone.utc)
        previous = [
            {
                "name": "index.yaml",
                "content_hash": "same",
                "updated_at": "2026-01-01T00:00:00+00:00",
            },
            {
                "name": "ti.yaml",
                "content_hash": "old",
                "updated_at": "2026-02-01T00:00:00+00:00",
            },
        ]
        entries = [
            {"name": "index.yaml", "content_hash": "same"},
            {"name": "ti.yaml", "content_hash": "new"},
            {"name": "nxp.yaml", "content_hash": "fresh"},
        ]

        stamped = apply_updated_at(entries, previous, now)

        self.assertEqual(stamped[0]["updated_at"], "2026-01-01T00:00:00+00:00")
        self.assertEqual(stamped[1]["updated_at"], now.isoformat())
        self.assertEqual(stamped[2]["updated_at"], now.isoformat())
