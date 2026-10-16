"""Load KernelCI hardware registry YAML into the hardware_registry_* tables."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import yaml
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

import requests
from kernelCI_app.models import (
    HardwareRegistryPlatform,
    HardwareRegistryPlatformVendor,
    HardwareRegistryProcessor,
    HardwareRegistrySiliconVendor,
    HardwareRegistrySync,
    HardwareRegistrySystemModule,
)

# Parents before children. Delete in reverse so FKs do not block the prune.
_WRITE_ORDER = (
    ("silicon_vendors", HardwareRegistrySiliconVendor),
    ("processors", HardwareRegistryProcessor),
    ("platform_vendors", HardwareRegistryPlatformVendor),
    ("system_modules", HardwareRegistrySystemModule),
    ("platforms", HardwareRegistryPlatform),
)


def get_update_fields(model):
    return [
        f.column if f.is_relation else f.name
        for f in model._meta.concrete_fields
        if not f.primary_key
    ]


def model_kwargs(model, raw: dict) -> dict:
    allowed = {field.attname for field in model._meta.concrete_fields}
    return {key: value for key, value in raw.items() if key in allowed}


def unwrap_registry(data: dict) -> dict:
    """Upstream nests every file under hardware_registry. Older files do not."""
    nested = data.get("hardware_registry")
    if isinstance(nested, dict):
        return nested
    return data


def file_name(source: str) -> str:
    return Path(urlparse(source).path).name


def sync_file_entry(source: str, raw: bytes) -> dict:
    return {
        "name": file_name(source),
        "url": source,
        "content_hash": hashlib.sha256(raw).hexdigest(),
    }


def apply_updated_at(entries: list[dict], previous: list, now) -> list[dict]:
    """Keep a file's updated_at when its bytes did not change."""
    previous_by_name = {item["name"]: item for item in previous}
    now_iso = now.isoformat()
    stamped = []
    for entry in entries:
        prior = previous_by_name.get(entry["name"])
        same_bytes = (
            prior is not None and prior["content_hash"] == entry["content_hash"]
        )
        stamped.append(
            {**entry, "updated_at": prior["updated_at"] if same_bytes else now_iso}
        )
    return stamped


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https")


class Command(BaseCommand):
    help = (
        "Load KernelCI hardware registry YAML "
        "(kernelci-pipeline config/hardware_registry/*.yaml) into the database. "
        "Accepts a local file path or a URL. --index records a per-file sync stamp."
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

    def _fetch_url(self, url: str) -> bytes:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.RequestException as exc:
            raise CommandError(f"Failed to fetch {url}: {exc}") from exc

    def _read_file(self, path: Path) -> bytes:
        if not path.is_file():
            raise CommandError(f"Registry file not found: {path}")
        try:
            return path.read_bytes()
        except OSError as exc:
            raise CommandError(f"Cannot read registry file: {exc}") from exc

    def _read_source(self, source: str) -> bytes:
        if _is_url(source):
            return self._fetch_url(source)
        return self._read_file(Path(source).expanduser().resolve())

    def load(self, source: str) -> tuple[bytes, dict]:
        raw = self._read_source(source)
        try:
            parsed = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise CommandError(f"Invalid YAML: {exc}") from exc

        if parsed is None:
            raise CommandError(f"Registry is empty or parses to null: {source}")
        if not isinstance(parsed, dict):
            raise CommandError(
                f"Expected a YAML mapping at root, got {type(parsed).__name__}: {source}"
            )
        return raw, unwrap_registry(parsed)

    def _resolve_relative(self, base: str, relative: str) -> str:
        if _is_url(base):
            return urljoin(base, relative)
        return str(Path(base).expanduser().resolve().parent / relative)

    def _registry_sources(self, index_source: str, data: dict) -> list[str]:
        entries = data.get("registries")
        if not isinstance(entries, list) or not entries:
            raise CommandError(
                "Index YAML must contain a 'registries' key with a non-empty list."
            )
        return [self._resolve_relative(index_source, entry) for entry in entries]

    def _persist_section(self, model, rows: dict, seen: set[str]) -> None:
        objects = []
        for key, raw in rows.items():
            if not isinstance(raw, dict):
                raise CommandError(
                    f"Expected a mapping for {model.__name__} entry {key!r}"
                )
            kwargs = model_kwargs(model, raw)
            seen.add(kwargs["id"])
            objects.append(model(**kwargs))
        model.objects.bulk_create(
            objects,
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=get_update_fields(model),
        )

    def _persist(self, source: str, data: dict, seen: dict[str, set[str]]) -> None:
        missing = [section for section, _model in _WRITE_ORDER if section not in data]
        if missing:
            self.stderr.write(
                self.style.WARNING(
                    f"Missing typical hardware-registry sections in {source}: "
                    f"{', '.join(missing)}"
                )
            )

        for section, model in _WRITE_ORDER:
            rows = data.get(section) or {}
            if not isinstance(rows, dict):
                raise CommandError(
                    f"Expected a mapping for {section} in {source}, "
                    f"got {type(rows).__name__}"
                )
            self._persist_section(model, rows, seen[section])

        self.stdout.write(self.style.SUCCESS(f"Processed: {source}"))

    def handle(self, *args: Any, **options: Any) -> None:
        registry_file = options.get("registry_file")
        index = options.get("index")

        if not registry_file and not index:
            raise CommandError("Provide either a registry_file or --index.")
        if registry_file and index:
            raise CommandError("Provide either a registry_file or --index, not both.")

        index_entry = None
        if index:
            index_raw, index_data = self.load(index)
            sources = self._registry_sources(index, index_data)
            index_entry = sync_file_entry(index, index_raw)
        else:
            sources = [registry_file]

        seen = {section: set() for section, _model in _WRITE_ORDER}
        entries = [index_entry] if index_entry else []

        with transaction.atomic():
            for source in sources:
                raw, data = self.load(source)
                self._persist(source, data, seen)
                entries.append(sync_file_entry(source, raw))

            if index_entry is None:
                return

            for _section, model in reversed(_WRITE_ORDER):
                model.objects.exclude(id__in=seen[_section]).delete()
            now = timezone.now()
            previous = HardwareRegistrySync.objects.filter(pk=1).first()
            HardwareRegistrySync.objects.update_or_create(
                id=1,
                defaults={
                    "synced_at": now,
                    "files": apply_updated_at(
                        entries,
                        [] if previous is None else previous.files,
                        now,
                    ),
                },
            )
            self.stdout.write(self.style.SUCCESS("Recorded hardware registry sync."))
