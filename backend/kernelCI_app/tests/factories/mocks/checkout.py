"""
Checkout data management class.
"""

from .fixtures import TREE_DATA


class Checkout:
    """Manages checkout test data and operations."""

    @classmethod
    def get_checkout_data(cls, checkout_id: str):
        """Get complete checkout data by ID."""
        return TREE_DATA.get(checkout_id)

    @classmethod
    def get_hardware_platform(cls, checkout_id: str):
        """Get hardware platform for a checkout."""
        checkout_data = TREE_DATA.get(checkout_id)
        return checkout_data.get("hardware_platform") if checkout_data else None

    @classmethod
    def get_timestamp(cls, checkout_id: str):
        """Get timestamp for a checkout."""
        checkout_data = TREE_DATA.get(checkout_id)
        return checkout_data.get("start_time") if checkout_data else None

    @classmethod
    def get_origin(cls, checkout_id: str):
        """Get origin for a checkout."""
        checkout_data = TREE_DATA.get(checkout_id)
        return checkout_data.get("origin") if checkout_data else None

    @classmethod
    def get_git_url(cls, checkout_id: str):
        """Get git URL for a checkout."""
        checkout_data = TREE_DATA.get(checkout_id)
        return checkout_data.get("git_url") if checkout_data else None

    @classmethod
    def get_git_branch(cls, checkout_id: str):
        """Get git branch for a checkout."""
        checkout_data = TREE_DATA.get(checkout_id)
        return checkout_data.get("git_branch") if checkout_data else None

    @classmethod
    def get_tree_name(cls, checkout_id: str):
        """Get tree name for a checkout."""
        checkout_data = TREE_DATA.get(checkout_id)
        return checkout_data.get("tree_name") if checkout_data else None

    @classmethod
    def get_all_checkout_ids(cls):
        """Get all checkout IDs from TREE_DATA."""
        return list(TREE_DATA.keys())

    @classmethod
    def is_known_checkout(cls, checkout_id: str):
        """Check if a checkout ID exists in TREE_DATA."""
        return checkout_id in TREE_DATA

    @classmethod
    def get_hardware_platform_from_data(cls, checkout_id: str):
        """Get hardware platform from TREE_DATA."""
        checkout_data = TREE_DATA.get(checkout_id)
        return checkout_data.get("hardware_platform") if checkout_data else None
