"""
Build data fixtures for test factories.
"""

EXPECTED_BUILD_IDS = {
    "maestro:67b62592f7707533c0ff7a77": {
        "checkout_id": "ef143cc9d68aecf16ec4942e399e7699266b288f",  # ANDROID_MAINLINE_TREE
        "origin": "maestro",
        "architecture": "x86_64",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "maestro:67b62592f7707533c0ff7a99": {
        "checkout_id": "a1c24ab822793eb513351686f631bd18952b7870",  # ARM64_TREE
        "origin": "maestro",
        "architecture": "x86_64",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "maestro:67b62592f7707533c0ff7a98": {
        "checkout_id": "a1c24ab822793eb513351686f631bd18952b7870",  # ARM64_TREE
        "origin": "maestro",
        "architecture": "x86_64",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "maestro:67b62592f7707533c0ff7a95": {
        "checkout_id": "a1c24ab822793eb513351686f631bd18952b7870",  # ARM64_TREE
        "origin": "maestro",
        "architecture": "x86_64",
        "status": "FAIL",
        "config_name": "defconfig",
    },
    "maestro:67b62592f7707533c0ff7a94": {
        "checkout_id": "a1c24ab822793eb513351686f631bd18952b7870",  # ARM64_TREE
        "origin": "maestro",
        "architecture": "x86_64",
        "status": "FAIL",
        "config_name": "defconfig",
    },
    "maestro:dummy_67cb759a180183719578307e_x86_64": {
        "checkout_id": "fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba",  # ANDROID_MAESTRO_MAINLINE
        "origin": "maestro",
        "architecture": "x86_64",
        "status": "FAIL",
        "config_name": "defconfig",
    },
    "maestro:67ce32e418018371957d36b1": {
        "checkout_id": "33040a50cdaec186c13ef3f7b9c9b668d8e32637",  # NEXT_PENDING_FIXES_BROONIE
        "origin": "broonie",
        "architecture": "arm64",
        "status": "FAIL",
        "config_name": "defconfig",
    },
    "redhat:1701576995-x86_64-kernel": {
        "checkout_id": "4b60a3c25e8793adfb1d92f8e4888321ae416fed",  # BROONIE_MISC_BROONIE
        "origin": "maestro",
        "architecture": "x86_64",
        "status": "FAIL",
        "config_name": "defconfig",
    },
    "google_juniper_build_valid": {
        "checkout_id": "google_juniper_checkout_001",
        "origin": "maestro",
        "architecture": "google,juniper",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "allwinner_build_valid": {
        "checkout_id": "5b4ec6e1eb7603b6d86a172d77efdf75eb741e7e",  # ALLWINNER_HARDWARE
        "origin": "maestro",
        "architecture": "allwinner,sun50i-a64",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "allwinner_build_valid_2": {
        "checkout_id": "0704a15b930cf97073ce091a0cd7ad32f2304329",  # ALLWINNER_HARDWARE
        "origin": "maestro",
        "architecture": "allwinner,sun50i-a64",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "arm_juno_build_valid": {
        "checkout_id": "arm_juno_checkout_001",
        "origin": "maestro",
        "architecture": "arm,juno",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "aaeon_build_valid": {
        "checkout_id": "aaeon_checkout_001",
        "origin": "maestro",
        "architecture": "i386",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "asus_build_valid": {
        "checkout_id": "asus_checkout_001",
        "origin": "maestro",
        "architecture": "asus-CM1400CXA-dalboz",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "amlogic_build_valid": {
        "checkout_id": "amlogic_checkout_001",
        "origin": "maestro",
        "architecture": "amlogic,g12b",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "android11-5.4": {
        "checkout_id": "7e39477098b50156535c8f910fee50d6dac2a793",  # android11-5.4
        "origin": "maestro",
        "architecture": "android11-5.4",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "android12-5.10": {
        "checkout_id": "4fd7634f32ffbb4fd4c09b757aa16327626a1749",  # android12-5.10
        "origin": "maestro",
        "architecture": "android12-5.10",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "android12-5.10-lts": {
        "checkout_id": "f72ba1ba267f4c42adb82037e8614d7844badeb9",  # android12-5.10-lts
        "origin": "maestro",
        "architecture": "android12-5.10-lts",
        "status": "PASS",
        "config_name": "defconfig",
    },
    "fluster_build_valid": {
        "checkout_id": "fluster_checkout_001",
        "origin": "maestro",
        "architecture": "arm64",
        "status": "PASS",
        "config_name": "defconfig+lab-setup+arm64-chromebook"
        + "+CONFIG_MODULE_COMPRESS=n+CONFIG_MODULE_COMPRESS_NONE=y",
    },
    "failed_tests_build": {
        "checkout_id": "failed_tests_checkout",
        "origin": "maestro",
        "architecture": "x86_64",
        "status": "FAIL",
        "config_name": "defconfig",
    },
    # TODO: Add builds to test STATUS NULL + add integration tests for this case
}

CHECKOUT_BUILD_STATUS_RULES = {
    # Checkouts that should make builds PASS
    "fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba": "PASS",  # ANDROID_MAESTRO_MAINLINE
    "33040a50cdaec186c13ef3f7b9c9b668d8e32637": "PASS",  # NEXT_PENDING_FIXES_BROONIE
    "4b60a3c25e8793adfb1d92f8e4888321ae416fed": "PASS",  # BROONIE_MISC_BROONIE
    "a1c24ab822793eb513351686f631bd18952b7870": "PASS",  # ARM64_TREE
    "5b4ec6e1eb7603b6d86a172d77efdf75eb741e7e": "PASS",  # ALLWINNER_HARDWARE
    "0704a15b930cf97073ce091a0cd7ad32f2304329": "PASS",  # ALLWINNER_HARDWARE
    "aaeon_checkout_001": "PASS",  # AAEON_HARDWARE
    "asus_checkout_001": "PASS",  # ASUS_HARDWARE
}
