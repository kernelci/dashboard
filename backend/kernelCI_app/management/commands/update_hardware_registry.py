"""Parse and display KernelCI hardware registry YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import yaml
from django.core.management.base import BaseCommand, CommandError

import requests
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


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https")


class Command(BaseCommand):
    help = (
        "Parse a KernelCI hardware registry YAML file (same shape as "
        "kernelci-pipeline config/hardware_registry/*.yaml) and print its data. "
        "Accepts a local file path or a URL."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "registry_file",
            nargs="?",
            type=str,
            help="Path or URL to a single hardware registry YAML file.",
        )
        parser.add_argument(
            "--index",
            type=str,
            help=(
                "Path or URL to an index YAML listing registry files "
                "(e.g. hardware_registry/index.yaml). Entries in the "
                "'registries' key are resolved relative to the index location."
            ),
        )

    def _fetch_url(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            raise CommandError(f"Failed to fetch {url}: {exc}") from exc

    def _read_file(self, path: Path) -> str:
        if not path.is_file():
            raise CommandError(f"Registry file not found: {path}")
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise CommandError(f"Cannot read registry file: {exc}") from exc

    def load_yaml(self, source: str) -> dict:
        if _is_url(source):
            raw = self._fetch_url(source)
        else:
            raw = self._read_file(Path(source).expanduser().resolve())

        try:
            return yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise CommandError(f"Invalid YAML: {exc}") from exc

    def _resolve_relative(self, base: str, relative: str) -> str:
        """Resolve a relative filename against the base index location."""
        if _is_url(base):
            return urljoin(base, relative)
        return str(Path(base).expanduser().resolve().parent / relative)

    def _resolve_index(self, index_source: str) -> list[str]:
        """Load an index YAML and return resolved paths/URLs for each registry."""
        data = self.load_yaml(index_source)
        if not isinstance(data, dict) or "registries" not in data:
            raise CommandError(
                "Index YAML must contain a 'registries' key with a list of filenames."
            )
        entries = data["registries"]
        if not isinstance(entries, list) or not entries:
            raise CommandError("Index 'registries' must be a non-empty list.")
        return [self._resolve_relative(index_source, entry) for entry in entries]

    def _process_registry(self, source: str) -> None:
        """Load and persist a single registry YAML."""
        data = self.load_yaml(source)

        if data is None:
            raise CommandError(f"Registry is empty or parses to null: {source}")
        if not isinstance(data, dict):
            raise CommandError(
                f"Expected a YAML mapping at root, got {type(data).__name__}: {source}"
            )

        missing = [k for k in EXPECTED_SECTIONS if k not in data]
        if missing:
            self.stderr.write(
                self.style.WARNING(
                    f"Missing typical hardware-registry sections in {source}: "
                    f"{', '.join(missing)}"
                )
            )

        silicon_vendors = data["silicon_vendors"] or {}
        platform_vendors = data["platform_vendors"] or {}
        processors = data["processors"] or {}
        system_modules = data["system_modules"] or {}
        platforms = data["platforms"] or {}

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

        self.stdout.write(self.style.SUCCESS(f"Processed: {source}"))

    def handle(self, *args: Any, **options: Any) -> None:
        registry_file = options.get("registry_file")
        index = options.get("index")

        if not registry_file and not index:
            raise CommandError("Provide either a registry_file or --index.")
        if registry_file and index:
            raise CommandError("Provide either a registry_file or --index, not both.")

        if index:
            sources = self._resolve_index(index)
        else:
            sources = [registry_file]

        for source in sources:
            self._process_registry(source)
