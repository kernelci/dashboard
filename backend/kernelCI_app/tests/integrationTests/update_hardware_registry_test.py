from datetime import datetime, timezone
from textwrap import dedent

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from kernelCI_app.models import (
    HardwareRegistryPlatform,
    HardwareRegistryPlatformVendor,
    HardwareRegistryProcessor,
    HardwareRegistrySiliconVendor,
    HardwareRegistrySync,
)


def _vendor_yaml(*platform_ids: str) -> str:
    platforms = "\n".join(
        "\n".join(
            [
                f"    {platform_id}:",
                f"      id: {platform_id}",
                "      type: evaluation_board",
                "      vendor_id: acme",
                "      processor_id: soc1",
                f'      compatible: ["acme,{platform_id}"]',
            ]
        )
        for platform_id in platform_ids
    )
    return (
        "hardware_registry:\n"
        "  silicon_vendors:\n"
        "    acme:\n"
        "      id: acme\n"
        "      type: silicon_vendor\n"
        "  platform_vendors:\n"
        "    acme:\n"
        "      id: acme\n"
        "      type: platform_vendor\n"
        "  processors:\n"
        "    soc1:\n"
        "      id: soc1\n"
        "      type: soc\n"
        "      vendor_id: acme\n"
        "  system_modules: {}\n"
        "  platforms:\n"
        f"{platforms}\n"
    )


def _write_index(tmp_path, vendor_name: str, platforms: list[str]) -> str:
    (tmp_path / vendor_name).write_text(_vendor_yaml(*platforms))
    index = tmp_path / "index.yaml"
    index.write_text(
        dedent(
            f"""
            hardware_registry:
              registries:
                - {vendor_name}
            """
        )
    )
    return str(index)


@pytest.mark.django_db
def test_failed_file_keeps_previous_rows_and_stamp(tmp_path):
    HardwareRegistrySiliconVendor.objects.create(id="old", type="silicon_vendor")
    HardwareRegistrySync.objects.create(
        id=1,
        synced_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        files=[{"name": "old.yaml", "url": "old", "content_hash": "abc", "counts": {}}],
    )
    index = tmp_path / "index.yaml"
    index.write_text(
        dedent(
            """
            hardware_registry:
              registries:
                - good.yaml
                - missing.yaml
            """
        )
    )
    (tmp_path / "good.yaml").write_text(_vendor_yaml("board-a"))

    with pytest.raises(CommandError):
        call_command("update_hardware_registry", index=str(index))

    assert list(HardwareRegistrySiliconVendor.objects.values_list("id", flat=True)) == [
        "old"
    ]
    assert not HardwareRegistryPlatform.objects.exists()
    stamp = HardwareRegistrySync.objects.get(pk=1)
    assert stamp.files[0]["name"] == "old.yaml"


@pytest.mark.django_db
def test_index_run_drops_platforms_missing_from_the_files(tmp_path):
    call_command(
        "update_hardware_registry",
        index=_write_index(tmp_path, "acme.yaml", ["board-a", "board-b"]),
    )
    assert set(HardwareRegistryPlatform.objects.values_list("id", flat=True)) == {
        "board-a",
        "board-b",
    }

    call_command(
        "update_hardware_registry",
        index=_write_index(tmp_path, "acme.yaml", ["board-a"]),
    )

    assert list(HardwareRegistryPlatform.objects.values_list("id", flat=True)) == [
        "board-a"
    ]
    assert HardwareRegistryPlatform.objects.get(id="board-a").compatible == [
        "acme,board-a"
    ]
    assert HardwareRegistryProcessor.objects.filter(id="soc1").exists()
    assert HardwareRegistryPlatformVendor.objects.filter(id="acme").exists()
    stamp = HardwareRegistrySync.objects.get(pk=1)
    assert [item["name"] for item in stamp.files] == ["index.yaml", "acme.yaml"]


@pytest.mark.django_db
def test_single_file_run_does_not_replace_the_stamp(tmp_path):
    HardwareRegistrySync.objects.create(
        id=1,
        synced_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        files=[{"name": "index.yaml", "url": "u", "content_hash": "abc", "counts": {}}],
    )
    silicon = HardwareRegistrySiliconVendor.objects.create(
        id="keep-sv", type="silicon_vendor"
    )
    vendor = HardwareRegistryPlatformVendor.objects.create(
        id="keep-pv", type="platform_vendor"
    )
    processor = HardwareRegistryProcessor.objects.create(
        id="keep-soc", type="soc", vendor=silicon
    )
    HardwareRegistryPlatform.objects.create(
        id="keep-board",
        type="evaluation_board",
        vendor=vendor,
        processor=processor,
    )
    registry = tmp_path / "one.yaml"
    registry.write_text(_vendor_yaml("board-a"))

    call_command("update_hardware_registry", str(registry))

    assert set(HardwareRegistryPlatform.objects.values_list("id", flat=True)) == {
        "keep-board",
        "board-a",
    }
    stamp = HardwareRegistrySync.objects.get(pk=1)
    assert stamp.files[0]["name"] == "index.yaml"
