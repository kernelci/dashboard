from types import SimpleNamespace
from unittest.mock import patch

from kernelCI_app.helpers.hardwareRegistry import (
    get_first_hardware_registry,
    get_hardware_registry_by_ids,
    serialize_hardware_registry_platform,
)


def _minimal_platform(platform_id: str):
    silicon = SimpleNamespace(id="ti", url="https://www.ti.com")
    processor = SimpleNamespace(
        id="am3358",
        architecture="arm",
        cores=1,
        max_clock_speed_mhz=800,
        url=None,
        details=None,
        vendor=silicon,
    )
    return SimpleNamespace(
        id=platform_id,
        type="board",
        form_factor=None,
        details=None,
        url=None,
        vendor=SimpleNamespace(id="ti", url=None),
        processor=processor,
        system_module=None,
    )


class TestGetHardwareRegistryByIds:
    def test_skips_query_when_no_usable_ids(self):
        with patch(
            "kernelCI_app.helpers.hardwareRegistry.HardwareRegistryPlatform.objects"
        ) as mock_objects:
            assert get_hardware_registry_by_ids([None, "", 1, {"a": 1}]) == {}
            mock_objects.select_related.assert_not_called()


class TestGetFirstHardwareRegistry:
    def test_returns_first_matching_id_in_order(self):
        platform = _minimal_platform("second")
        with patch(
            "kernelCI_app.helpers.hardwareRegistry.get_hardware_registry_by_ids"
        ) as mock_by_ids:
            mock_by_ids.return_value = {
                "second": serialize_hardware_registry_platform(platform)
            }
            info = get_first_hardware_registry([None, "missing", "second", "third"])

        assert info is not None
        assert info.platform_id == "second"
