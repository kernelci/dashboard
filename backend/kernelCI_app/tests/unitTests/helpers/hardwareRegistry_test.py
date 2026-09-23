from types import SimpleNamespace
from unittest.mock import patch

from kernelCI_app.helpers.hardwareRegistry import (
    get_first_hardware_registry,
    get_hardware_registry_by_ids,
    serialize_hardware_registry_platform,
)


def _platform(**overrides):
    silicon = SimpleNamespace(id="ti", url="https://www.ti.com")
    processor = SimpleNamespace(
        id="am3358",
        architecture="arm",
        cores=1,
        max_clock_speed_mhz=800,
        url="https://www.ti.com/product/AM3358",
        details="Arm Cortex-A8",
        vendor=silicon,
    )
    values = {
        "id": "am335x-bone-black",
        "type": "single_board_computer",
        "form_factor": "board",
        "details": "BeagleBone Black",
        "url": "https://beagleboard.org/black",
        "vendor": SimpleNamespace(id="beagleboard", url="https://beagleboard.org"),
        "processor": processor,
        "system_module": SimpleNamespace(
            id="osd335x",
            url="https://octavosystems.com",
            form_factor="system-on-module",
        ),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class TestSerializeHardwareRegistryPlatform:
    def test_maps_related_fields(self):
        info = serialize_hardware_registry_platform(_platform())

        assert info.platform_id == "am335x-bone-black"
        assert info.board_type == "single_board_computer"
        assert info.processor.id == "am3358"
        assert info.processor.max_clock_speed_mhz == 800
        assert info.silicon_vendor.id == "ti"
        assert info.vendor.id == "beagleboard"
        assert info.system_module.id == "osd335x"

    def test_keeps_optional_relations_absent(self):
        info = serialize_hardware_registry_platform(_platform(system_module=None))

        assert info.system_module is None


class TestGetHardwareRegistryByIds:
    def test_skips_query_when_no_usable_ids(self):
        with patch(
            "kernelCI_app.helpers.hardwareRegistry.HardwareRegistryPlatform.objects"
        ) as mock_objects:
            assert get_hardware_registry_by_ids([None, "", 1, {"a": 1}]) == {}
            mock_objects.select_related.assert_not_called()

    def test_indexes_serialized_platforms(self):
        platform = _platform()
        with patch(
            "kernelCI_app.helpers.hardwareRegistry.HardwareRegistryPlatform.objects"
        ) as mock_objects:
            mock_objects.select_related.return_value.filter.return_value = [platform]
            result = get_hardware_registry_by_ids(["am335x-bone-black"])

        assert list(result) == ["am335x-bone-black"]
        assert result["am335x-bone-black"].processor.id == "am3358"


class TestGetFirstHardwareRegistry:
    def test_returns_first_matching_id_in_order(self):
        platform = _platform(id="second")
        with patch(
            "kernelCI_app.helpers.hardwareRegistry.get_hardware_registry_by_ids"
        ) as mock_by_ids:
            mock_by_ids.return_value = {
                "second": serialize_hardware_registry_platform(platform)
            }
            info = get_first_hardware_registry([None, "missing", "second", "third"])

        assert info is not None
        assert info.platform_id == "second"
