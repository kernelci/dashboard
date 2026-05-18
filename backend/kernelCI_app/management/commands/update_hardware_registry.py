"""Parse and display KernelCI hardware registry YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from django.core.management.base import BaseCommand, CommandError

from kernelCI_app.models import (
    HardwareRegistryPlatform,
    HardwareRegistryPlatformVendor,
    HardwareRegistryProcessor,
    HardwareRegistrySiliconVendor,
    HardwareRegistrySystemModule,
)


def get_update_fields(model):
    return [
        f.column if f.is_relation else f.name
        for f in model._meta.concrete_fields
        if not f.primary_key
    ]


EXPECTED_SECTIONS = (
    "silicon_vendors",
    "platform_vendors",
    "processors",
    "system_modules",
    "platforms",
)


class Command(BaseCommand):
    help = (
        "Parse a KernelCI hardware registry YAML file (same shape as "
        "kernelci-pipeline config/hardware_registry/*.yaml) and print its data."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "registry_file",
            type=str,
            help="Path to the hardware registry YAML file.",
        )

    def load_yaml(self, path: str) -> dict:
        if not path.is_file():
            raise CommandError(f"Registry file not found: {path}")
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise CommandError(f"Cannot read registry file: {exc}") from exc

        try:
            data = yaml.safe_load(raw)
            return data
        except yaml.YAMLError as exc:
            raise CommandError(f"Invalid YAML: {exc}") from exc

    def handle(self, *args: Any, registry_file: str, **options: Any) -> None:
        path = Path(registry_file).expanduser().resolve()
        data = self.load_yaml(path)

        if data is None:
            raise CommandError("Registry file is empty or parses to null.")
        if not isinstance(data, dict):
            raise CommandError(
                f"Expected a YAML mapping at root, got {type(data).__name__}."
            )

        missing = [k for k in EXPECTED_SECTIONS if k not in data]
        if missing:
            self.stderr.write(
                self.style.WARNING(
                    f"Missing typical hardware-registry sections : {', '.join(missing)}"
                )
            )

        silicon_vendors = data["silicon_vendors"] or []
        platform_vendors = data["platform_vendors"] or []
        processors = data["processors"] or []
        system_modules = data["system_modules"] or []
        platforms = data["platforms"] or []

        HardwareRegistrySiliconVendor.objects.bulk_create(
            [HardwareRegistrySiliconVendor(**sv) for sv in silicon_vendors.values()],
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=get_update_fields(HardwareRegistrySiliconVendor),
        )

        HardwareRegistryProcessor.objects.bulk_create(
            [HardwareRegistryProcessor(**p) for p in processors.values()],
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=get_update_fields(HardwareRegistryProcessor),
        )

        HardwareRegistryPlatformVendor.objects.bulk_create(
            [HardwareRegistryPlatformVendor(**pv) for pv in platform_vendors.values()],
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=get_update_fields(HardwareRegistryPlatformVendor),
        )

        HardwareRegistrySystemModule.objects.bulk_create(
            [HardwareRegistrySystemModule(**sm) for sm in system_modules.values()],
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=get_update_fields(HardwareRegistrySystemModule),
        )

        HardwareRegistryPlatform.objects.bulk_create(
            [HardwareRegistryPlatform(**p) for p in platforms.values()],
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=get_update_fields(HardwareRegistryPlatform),
        )
