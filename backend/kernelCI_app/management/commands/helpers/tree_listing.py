from datetime import datetime
from typing import Any, NamedTuple


class CheckoutRow(NamedTuple):
    checkout_id: str
    origin: str
    tree_name: str | None
    git_repository_url: str | None
    git_repository_branch: str | None
    git_commit_hash: str | None
    git_commit_name: str | None
    git_commit_tags: list[str] | None
    start_time: datetime | None


class TreeListingRow(NamedTuple):
    """Flat row passed to cursor.executemany() for UPDATE tree_listing.

    Field order must match the SQL parameter placeholders in _process_tree_listing.
    """

    build_pass: int
    build_failed: int
    build_inc: int
    boot_pass: int
    boot_failed: int
    boot_inc: int
    test_pass: int
    test_failed: int
    test_inc: int
    origin: str
    tree_name: str | None
    git_repository_branch: str | None
    git_repository_url: str | None
    git_commit_hash: str | None


def tree_listing_sort_key(v: Any) -> tuple:
    """Sort key for tree_listing rows by unique constraint columns.

    Ensures deterministic lock acquisition order in concurrent transactions,
    preventing deadlocks between the ingester and aggregation processor.
    Compatible with both CheckoutRow and TreeListingRow.
    """
    return (
        (v.origin is None, v.origin or ""),
        (v.tree_name is None, v.tree_name or ""),
        (v.git_repository_url is None, v.git_repository_url or ""),
        (v.git_repository_branch is None, v.git_repository_branch or ""),
        (v.git_commit_hash is None, v.git_commit_hash or ""),
    )
