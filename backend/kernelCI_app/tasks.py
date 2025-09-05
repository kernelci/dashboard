from kernelCI_app.models import Checkouts
from kernelCI_app.queries.tree import (
    get_tree_listing_data_by_checkout_id,
    get_tree_listing_fast,
)
from kernelCI_cache.checkouts import populate_checkouts_cache_db
from kernelCI_cache.constants import NO_CACHE_ORIGINS, UNSTABLE_CHECKOUT_THRESHOLD
from kernelCI_cache.queries.checkouts import get_cached_tree_listing_fast
from datetime import timedelta
from django.utils.timezone import now, make_aware

UPDATE_INTERVAL_IN_DAYS = 90

type TreeIdentifier = tuple[str | None, str | None, str | None]
"""A tuple to identify a unique tree: (tree_name, git_repository_branch, git_repository_url)"""


def _is_checkout_done(*, checkout: dict | Checkouts) -> bool:
    if isinstance(checkout, Checkouts):
        origin_builds_finish_time = checkout.origin_builds_finish_time
        origin_tests_finish_time = checkout.origin_tests_finish_time
    else:
        origin_builds_finish_time = checkout["origin_builds_finish_time"]
        origin_tests_finish_time = checkout["origin_tests_finish_time"]

    return (
        origin_builds_finish_time is not None and origin_tests_finish_time is not None
    )


def _is_checkout_unstable(*, checkout: dict | Checkouts) -> bool:
    """
    Defines if a checkout is considered unstable or not.

    It will be *stable* if both origin_builds_finish_time and origin_tests_finish_time are set
      or if it is older than UNSTABLE_CHECKOUT_THRESHOLD.

    Returns True if unstable, False if stable.
    """
    unstable_threshold = now() - timedelta(days=UNSTABLE_CHECKOUT_THRESHOLD)
    if isinstance(checkout, Checkouts):
        start_time = checkout.start_time
    else:
        start_time = checkout["start_time"]

    is_old = start_time is not None and start_time < unstable_threshold
    is_done = _is_checkout_done(checkout=checkout)
    if is_old or is_done:
        return False
    else:
        return True


def get_checkout_ids_for_update(
    *,
    kcidb_checkouts: list[Checkouts],
    sqlite_tree_keys: set[TreeIdentifier],
    sqlite_trees_map: dict[TreeIdentifier, dict],
) -> set[str]:
    checkout_ids_for_update = set()

    for checkout in kcidb_checkouts:
        if checkout.origin in NO_CACHE_ORIGINS:
            continue

        checkout_key: TreeIdentifier = (
            checkout.tree_name,
            checkout.git_repository_branch,
            checkout.git_repository_url,
        )

        # If the equivalent tree in sqlite is unstable, update it nonetheless
        same_tree_on_sqlite = sqlite_trees_map.get(checkout_key)
        if same_tree_on_sqlite["unstable"]:
            checkout_ids_for_update.add(same_tree_on_sqlite["checkout_id"])

        # Trees that aren't in the sqlite should be added
        if checkout_key not in sqlite_tree_keys:
            checkout_ids_for_update.add(checkout.id)
            continue

        # If the current checkout is unstable, update it
        if _is_checkout_unstable(checkout=checkout):
            checkout_ids_for_update.add(checkout.id)
            continue

        # Even if the current checkout is stable, if it is newer than the cached one, update it
        cached_start_time = same_tree_on_sqlite["start_time"]
        if cached_start_time is not None:
            if cached_start_time.tzinfo is None:
                cached_start_time = make_aware(cached_start_time)
            if checkout.start_time > cached_start_time:
                checkout_ids_for_update.add(checkout.id)
                continue

    return checkout_ids_for_update


def update_checkout_cache():
    checkout_ids_for_update: set[str] = set()

    kcidb_checkouts = get_tree_listing_fast(interval={"days": UPDATE_INTERVAL_IN_DAYS})

    sqlite_checkouts = get_cached_tree_listing_fast()
    sqlite_trees_map: dict[TreeIdentifier, dict] = {}
    sqlite_tree_keys: set[TreeIdentifier] = set()
    for cached_checkout in sqlite_checkouts:
        tree_ident: TreeIdentifier = (
            cached_checkout["tree_name"],
            cached_checkout["git_repository_branch"],
            cached_checkout["git_repository_url"],
        )
        sqlite_tree_keys.add(tree_ident)
        sqlite_trees_map[tree_ident] = cached_checkout

    checkout_ids_for_update = get_checkout_ids_for_update(
        kcidb_checkouts=kcidb_checkouts,
        sqlite_tree_keys=sqlite_tree_keys,
        sqlite_trees_map=sqlite_trees_map,
    )

    updated_checkouts_data = get_tree_listing_data_by_checkout_id(
        checkout_ids=list(checkout_ids_for_update),
    )

    for checkout in updated_checkouts_data:
        checkout["unstable"] = _is_checkout_unstable(checkout=checkout)

    populate_checkouts_cache_db(data=updated_checkouts_data)
