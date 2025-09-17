"""
Build data management class.
"""

from .fixtures import EXPECTED_BUILD_IDS, CHECKOUT_BUILD_STATUS_RULES


class Build:
    """Manages build test data and operations."""

    @classmethod
    def get_build_data(cls, build_id: str):
        """Get complete build data by ID."""
        return EXPECTED_BUILD_IDS.get(build_id)

    @classmethod
    def get_build_status(cls, build_id: str):
        """Get build status by ID."""
        build_data = EXPECTED_BUILD_IDS.get(build_id)
        return build_data.get("status") if build_data else None

    @classmethod
    def get_build_checkout_id(cls, build_id: str):
        """Get checkout ID for a build."""
        build_data = EXPECTED_BUILD_IDS.get(build_id)
        return build_data.get("checkout_id") if build_data else None

    @classmethod
    def get_build_origin(cls, build_id: str):
        """Get origin for a build."""
        build_data = EXPECTED_BUILD_IDS.get(build_id)
        return build_data.get("origin") if build_data else None

    @classmethod
    def get_build_architecture(cls, build_id: str):
        """Get architecture for a build."""
        build_data = EXPECTED_BUILD_IDS.get(build_id)
        return build_data.get("architecture") if build_data else None

    @classmethod
    def get_build_config_name(cls, build_id: str):
        """Get config name for a build."""
        build_data = EXPECTED_BUILD_IDS.get(build_id)
        return build_data.get("config_name") if build_data else None

    @classmethod
    def get_builds_for_checkout(cls, checkout_id: str):
        """Get all build IDs for a specific checkout."""
        return [
            build_id
            for build_id, build_data in EXPECTED_BUILD_IDS.items()
            if build_data.get("checkout_id") == checkout_id
        ]

    @classmethod
    def get_build_status_from_rules(cls, build_id: str, checkout_id: str):
        """Get build status using rules (build-specific first, then checkout-based)."""
        build_data = EXPECTED_BUILD_IDS.get(build_id)
        if build_data and "status" in build_data:
            return build_data["status"]

        return CHECKOUT_BUILD_STATUS_RULES.get(checkout_id)

    @classmethod
    def get_all_build_ids(cls):
        """Get all build IDs from EXPECTED_BUILD_IDS."""
        return list(EXPECTED_BUILD_IDS.keys())

    @classmethod
    def is_known_build(cls, build_id: str):
        """Check if a build ID exists in EXPECTED_BUILD_IDS."""
        return build_id in EXPECTED_BUILD_IDS
