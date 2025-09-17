"""
Test data management class.
"""

from .fixtures import TEST_DATA, BUILD_TEST_STATUS_RULES, CHECKOUT_TEST_STATUS_RULES


class Test:
    """Manages test data and operations."""

    @classmethod
    def get_test_data(cls, test_id: str):
        """Get complete test data by ID."""
        return TEST_DATA.get(test_id)

    @classmethod
    def get_test_status(cls, test_id: str):
        """Get test status by ID."""
        test_data = TEST_DATA.get(test_id)
        return test_data.get("status") if test_data else None

    @classmethod
    def get_test_path(cls, test_id: str):
        """Get path for a test."""
        test_data = TEST_DATA.get(test_id)
        return test_data.get("path") if test_data else None

    @classmethod
    def get_test_status_from_rules(cls, test_id: str, build_id: str, checkout_id: str):
        """Get test status using rules (test-specific first, then build-based, then checkout-based)."""
        test_data = TEST_DATA.get(test_id)
        if test_data and "status" in test_data:
            return test_data["status"]

        build_status = BUILD_TEST_STATUS_RULES.get(build_id)
        if build_status:
            return build_status

        return CHECKOUT_TEST_STATUS_RULES.get(checkout_id)

    @classmethod
    def get_all_test_ids(cls):
        """Get all test IDs from TEST_DATA."""
        return list(TEST_DATA.keys())

    @classmethod
    def is_known_test(cls, test_id: str):
        """Check if a test ID exists in TEST_DATA."""
        return test_id in TEST_DATA
