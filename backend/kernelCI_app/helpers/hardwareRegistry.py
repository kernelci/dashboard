from typing import Iterable, Optional

from kernelCI_app.models import HardwareRegistryPlatform
from kernelCI_app.typeModels.hardwareRegistry import (
    HardwareRegistryInfo,
    HardwareRegistryNamedLink,
    HardwareRegistryProcessorInfo,
)


def serialize_hardware_registry_platform(
    platform: HardwareRegistryPlatform,
) -> HardwareRegistryInfo:
    processor = platform.processor
    system_module = platform.system_module

    return HardwareRegistryInfo(
        platform_id=platform.id,
        board_type=platform.type,
        form_factor=platform.form_factor,
        description=platform.details,
        url=platform.url,
        vendor=HardwareRegistryNamedLink(
            id=platform.vendor.id, url=platform.vendor.url
        ),
        silicon_vendor=HardwareRegistryNamedLink(
            id=processor.vendor.id, url=processor.vendor.url
        ),
        system_module=(
            HardwareRegistryNamedLink(
                id=system_module.id,
                url=system_module.url,
                form_factor=system_module.form_factor,
            )
            if system_module
            else None
        ),
        processor=HardwareRegistryProcessorInfo(
            id=processor.id,
            architecture=processor.architecture,
            cores=processor.cores,
            max_clock_speed_mhz=processor.max_clock_speed_mhz,
            url=processor.url,
            description=processor.details,
        ),
    )


def _platform_ids(values: Iterable[object]) -> list[str]:
    """Unique, non-empty platform ids. environment_misc values can be anything."""
    return list(dict.fromkeys(v for v in values if isinstance(v, str) and v))


def get_hardware_registry_by_ids(
    platform_ids: Iterable[object],
) -> dict[str, HardwareRegistryInfo]:
    ids = _platform_ids(platform_ids)
    if not ids:
        return {}

    platforms = HardwareRegistryPlatform.objects.select_related(
        "vendor",
        "processor",
        "processor__vendor",
        "system_module",
    ).filter(id__in=ids)

    return {
        platform.id: serialize_hardware_registry_platform(platform)
        for platform in platforms
    }


def get_first_hardware_registry(
    platform_ids: Iterable[object],
) -> Optional[HardwareRegistryInfo]:
    """Registry info for the first id that the registry knows about."""
    ids = _platform_ids(platform_ids)
    by_id = get_hardware_registry_by_ids(ids)
    return next((by_id[pid] for pid in ids if pid in by_id), None)
