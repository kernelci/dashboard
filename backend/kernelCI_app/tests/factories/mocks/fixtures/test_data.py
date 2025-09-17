"""
Test data fixtures for test factories.
"""

TEST_DATA = {
    "maestro:67b898cdf7707533c0067a02": {
        "status": "FAIL",
        "path": None,
    },
    "maestro:67bd70e6323b35c54a8824a0": {
        "status": "FAIL",
        "path": None,
    },
    "test_issue_test": {
        "status": "FAIL",
        "path": None,
    },
}

BUILD_TEST_STATUS_RULES = {
    # Builds that should make tests FAIL
    "maestro:67b62592f7707533c0ff7a99": "FAIL",
    "maestro:67b62592f7707533c0ff7a98": "FAIL",
    "maestro:67b62592f7707533c0ff7a95": "FAIL",
    "maestro:67b62592f7707533c0ff7a94": "FAIL",
    "asus_build_valid": "FAIL",
    # Builds that should make tests PASS
    "google_juniper_build_valid": "PASS",
    "allwinner_build_valid": "PASS",
    "allwinner_build_valid_2": "PASS",
    "arm_juno_build_valid": "PASS",
    "aaeon_build_valid": "PASS",
    "amlogic_build_valid": "PASS",
    "fluster_build_valid": "PASS",
}

CHECKOUT_TEST_STATUS_RULES = {
    # Checkouts that should make tests SKIP
    "4b60a3c25e8793adfb1d92f8e4888321ae416fed": "SKIP",  # BROONIE_MISC_BROONIE
    # Checkouts that should make tests PASS
    "fdf4d20b86285d7b4d1c2d3349a1bd1bc41b24ba": "PASS",  # ANDROID_MAESTRO_MAINLINE
    "33040a50cdaec186c13ef3f7b9c9b668d8e32637": "PASS",  # NEXT_PENDING_FIXES_BROONIE
    "5b4ec6e1eb7603b6d86a172d77efdf75eb741e7e": "PASS",  # ALLWINNER_HARDWARE
    "0704a15b930cf97073ce091a0cd7ad32f2304329": "PASS",  # ALLWINNER_HARDWARE
}
