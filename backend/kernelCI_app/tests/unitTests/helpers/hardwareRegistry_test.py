from types import SimpleNamespace
from typing import Optional
from unittest.mock import patch

from kernelCI_app.helpers.hardwareRegistry import (
    get_first_hardware_registry,
    get_hardware_registry_by_ids,
    serialize_hardware_registry_platform,
)


def _minimal_platform(platform_id: str, compatible: Optional[list[str]] = None):
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
        compatible=compatible,
    )


class TestGetHardwareRegistryByIds:
    def test_skips_query_when_no_usable_ids(self):
        with patch(
            "kernelCI_app.helpers.hardwareRegistry.HardwareRegistryPlatform.objects"
        ) as mock_objects:
            assert get_hardware_registry_by_ids([None, "", 1, {"a": 1}]) == {}
            mock_objects.select_related.assert_not_called()

    def test_maps_a_name_to_one_board(self):
        am62 = _minimal_platform("am62-sk", ["ti,am625-sk", "ti,am625"])
        lp = _minimal_platform("am62-lp-sk", ["ti,am62-lp-sk", "ti,am625"])
        with patch(
            "kernelCI_app.helpers.hardwareRegistry.HardwareRegistryPlatform.objects"
        ) as mock_objects:
            mock_objects.select_related.return_value.filter.return_value = [am62, lp]
            found = get_hardware_registry_by_ids(
                ["ti,am625-sk", "ti,am62-sk", "ti,am625", "am62-sk", "bcm2711-rpi-4-b"]
            )

        assert set(found) == {"ti,am625-sk", "ti,am62-sk", "am62-sk"}
        assert found["ti,am625-sk"].platform_id == "am62-sk"
        assert found["ti,am62-sk"].platform_id == "am62-sk"
        assert found["am62-sk"].platform_id == "am62-sk"


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

    def test_skips_a_shared_compatible_and_uses_the_next_name(self):
        am62 = _minimal_platform("am62-sk", ["ti,am625-sk", "ti,am625"])
        lp = _minimal_platform("am62-lp-sk", ["ti,am62-lp-sk", "ti,am625"])
        with patch(
            "kernelCI_app.helpers.hardwareRegistry.HardwareRegistryPlatform.objects"
        ) as mock_objects:
            mock_objects.select_related.return_value.filter.return_value = [am62, lp]
            info = get_first_hardware_registry(["ti,am625", "ti,am625-sk"])

        assert info is not None
        assert info.platform_id == "am62-sk"
