from kernelCI_app.typeModels.common import StatusCount
from kernelCI_app.typeModels.hardwareListing import HardwareItem


def sanitize_hardware(
    hardware: dict,
) -> HardwareItem:
    """Sanitizes a HardwareItem that was returned by a 'hardwarelisting-like' query

    Returns a HardwareItem object"""
    hardware_name = hardware["hardware"]
    platform = hardware["platform"]

    build_status_summary = StatusCount(
        PASS=hardware["pass_builds"],
        FAIL=hardware["fail_builds"],
        NULL=hardware["null_builds"],
        ERROR=hardware["error_builds"],
        MISS=hardware["miss_builds"],
        DONE=hardware["done_builds"],
        SKIP=hardware["skip_builds"],
    )

    test_status_summary = StatusCount(
        PASS=hardware["pass_tests"],
        FAIL=hardware["fail_tests"],
        NULL=hardware["null_tests"],
        ERROR=hardware["error_tests"],
        MISS=hardware["miss_tests"],
        DONE=hardware["done_tests"],
        SKIP=hardware["skip_tests"],
    )

    boot_status_summary = StatusCount(
        PASS=hardware["pass_boots"],
        FAIL=hardware["fail_boots"],
        NULL=hardware["null_boots"],
        ERROR=hardware["error_boots"],
        MISS=hardware["miss_boots"],
        DONE=hardware["done_boots"],
        SKIP=hardware["skip_boots"],
    )

    return HardwareItem(
        hardware=hardware_name,
        platform=platform,
        test_status_summary=test_status_summary,
        boot_status_summary=boot_status_summary,
        build_status_summary=build_status_summary,
    )
