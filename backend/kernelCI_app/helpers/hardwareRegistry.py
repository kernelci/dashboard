from typing import Iterable, Optional

from django.db.models import Q

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
            HardwareRegistryNamedLink(id=system_module.id, url=system_module.url)
            if system_module
            else None
        ),
        processor=HardwareRegistryProcessorInfo(
            id=processor.id,
            architecture=processor.architecture,
            cores=processor.cores,
            max_clock_speed_mhz=processor.max_clock_speed_mhz,
            url=processor.url,
        ),
    )


def _platform_ids(values: Iterable[object]) -> list[str]:
    return list(dict.fromkeys(v for v in values if isinstance(v, str) and v))


def get_hardware_registry_by_ids(
    platform_ids: Iterable[object],
) -> dict[str, HardwareRegistryInfo]:
    """One board per name: the id, the id after a comma, or a compatible string
    that only one board has. A shared compatible matches nothing."""
    names = _platform_ids(platform_ids)
    if not names:
        return {}

    suffixes = [name.split(",", 1)[-1] for name in names]
    platforms = list(
        HardwareRegistryPlatform.objects.select_related(
            "vendor", "processor", "processor__vendor", "system_module"
        ).filter(Q(id__in={*names, *suffixes}) | Q(compatible__overlap=names))
    )
    by_id = {platform.id: platform for platform in platforms}
    wanted = set(names)
    # None marks a compatible string that belongs to more than one board.
    hits: dict[str, Optional[HardwareRegistryPlatform]] = {}
    for platform in platforms:
        for compatible in platform.compatible or ():
            if compatible in wanted:
                hits[compatible] = None if compatible in hits else platform

    resolved: dict[str, HardwareRegistryInfo] = {}
    for name in names:
        platform = (
            by_id.get(name) or by_id.get(name.split(",", 1)[-1]) or hits.get(name)
        )
        if platform is not None:
            resolved[name] = serialize_hardware_registry_platform(platform)
    return resolved


def get_first_hardware_registry(
    platform_ids: Iterable[object],
) -> Optional[HardwareRegistryInfo]:
    found = get_hardware_registry_by_ids(platform_ids)
    return next(
        (found[name] for name in _platform_ids(platform_ids) if name in found),
        None,
    )
