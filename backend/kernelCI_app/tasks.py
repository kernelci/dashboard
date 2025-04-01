import os

from kernelCI_app.models import Checkouts
from kernelCI_app.queries.tree import (
    get_tree_listing_data_by_checkout_id,
    get_tree_listing_fast,
)
from kernelCI_cache.checkouts import populate_checkouts_cache_db
from kernelCI_cache.queries.checkouts import get_all_checkout_ids
from datetime import timedelta
from django.utils.timezone import now


def example_task():
    """
    Example task that increments a counter file.\n
    This is a temporary example until we have real tasks. It can be deleted once that happens.
    """
    counter_file = os.path.join(os.path.dirname(__file__), "counter.txt")

    try:
        with open(counter_file, "r") as file:
            counter = int(file.read().strip())
    except FileNotFoundError:
        counter = 0

    counter += 1

    with open(counter_file, "w") as file:
        file.write(str(counter))


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
    three_days_ago = now() - timedelta(days=3)
    if isinstance(checkout, Checkouts):
        start_time = checkout.start_time
    else:
        start_time = checkout["start_time"]

    is_old = start_time is not None and start_time < three_days_ago
    is_done = _is_checkout_done(checkout=checkout)
    if is_old or is_done:
        return False
    else:
        return True


def update_checkout_cache():
    checkout_ids_for_update: list[str] = []

    all_kcidb_checkouts = get_tree_listing_fast(interval={"days": 90})

    all_sqlite_checkout_ids_records = get_all_checkout_ids()
    all_sqlite_checkout_ids = [
        record["checkout_id"] for record in all_sqlite_checkout_ids_records
    ]

    for checkout in all_kcidb_checkouts:
        if not isinstance(checkout, Checkouts):
            continue

        if checkout.id not in all_sqlite_checkout_ids:
            checkout_ids_for_update.append(checkout.id)
            continue

        is_unstable = _is_checkout_unstable(checkout=checkout)

        if is_unstable:
            checkout_ids_for_update.append(checkout.id)

    updated_checkouts_data = get_tree_listing_data_by_checkout_id(
        checkout_ids=checkout_ids_for_update,
    )

    for checkout in updated_checkouts_data:
        checkout["unstable"] = _is_checkout_unstable(checkout=checkout)

    populate_checkouts_cache_db(data=updated_checkouts_data)
