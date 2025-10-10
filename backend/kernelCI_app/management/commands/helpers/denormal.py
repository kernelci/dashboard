from datetime import datetime
from django.db import connections
from kernelCI_app.models import Checkouts, TreeListing


def handle_checkout_denormalization(*, buffer: list[Checkouts]) -> None:
    """Deals with the operations related to the extra tables for denormalization.

    In the case of checkouts, it will update TreeListing table, and consume from PendingCheckouts.
    """

    if not buffer:
        return

    tuple_params = [
        (c.origin, c.tree_name, c.git_repository_branch, c.git_repository_url)
        for c in buffer
    ]
    flattened_list = []
    for tuple in tuple_params:
        flattened_list += list(tuple)

    # check if the tree already exists on TreeListing // check which trees exist
    query = f"""
        SELECT
            checkout_id,
            start_time
        FROM
            tree_listing t
        JOIN
            (VALUES {','.join(["(%s, %s, %s, %s)"] * len(tuple_params))})
            AS v(origin, tree_name, git_repository_branch, git_repository_url)
            ON (
                t.origin = v.origin
                AND t.tree_name = v.tree_name
                AND t.git_repository_branch = v.git_repository_branch
                AND t.git_repository_url = v.git_repository_url
            )
    """

    with connections["default"].cursor() as cursor:
        cursor.execute(query, flattened_list)
        results = cursor.fetchall()

    existing_checkouts_map = {r[0]: r[1] for r in results}

    checkouts_for_update: list[Checkouts] = []

    # results now have the list of checkout_id that *are* in the TreeListing
    for checkout in buffer:
        # if the checkout is in treeListing, check the start_time
        if checkout.id in existing_checkouts_map:
            # if newer than existing, update
            checkout_start_time = datetime.fromisoformat(checkout.start_time)
            if checkout_start_time >= existing_checkouts_map[checkout.id]:
                checkouts_for_update.append(checkout)
            # if older than existing, ignore (no action)
        # if it's not on treeListing, add it
        else:
            checkouts_for_update.append(checkout)

    if checkouts_for_update:
        tree_listing_objects = [
            TreeListing(
                field_timestamp=checkout.field_timestamp,
                checkout_id=checkout.id,
                origin=checkout.origin,
                tree_name=checkout.tree_name,
                git_repository_url=checkout.git_repository_url,
                git_repository_branch=checkout.git_repository_branch,
                git_commit_hash=checkout.git_commit_hash,
                git_commit_name=checkout.git_commit_name,
                git_commit_tags=checkout.git_commit_tags,
                start_time=checkout.start_time,
                origin_builds_finish_time=checkout.origin_builds_finish_time,
                origin_tests_finish_time=checkout.origin_tests_finish_time,
                # Countings are defaulted to 0 when not provided
            )
            for checkout in checkouts_for_update
        ]

        TreeListing.objects.bulk_create(
            tree_listing_objects,
            update_conflicts=True,
            unique_fields=[
                "origin",
                "tree_name",
                "git_repository_branch",
                "git_repository_url",
            ],
            update_fields=[
                "field_timestamp",
                "checkout_id",
                "origin",
                "tree_name",
                "git_repository_url",
                "git_repository_branch",
                "git_commit_hash",
                "git_commit_name",
                "git_commit_tags",
                "start_time",
                "origin_builds_finish_time",
                "origin_tests_finish_time",
                "pass_builds",
                "fail_builds",
                "done_builds",
                "miss_builds",
                "skip_builds",
                "error_builds",
                "null_builds",
                "pass_boots",
                "fail_boots",
                "done_boots",
                "miss_boots",
                "skip_boots",
                "error_boots",
                "null_boots",
                "pass_tests",
                "fail_tests",
                "done_tests",
                "miss_tests",
                "skip_tests",
                "error_tests",
                "null_tests",
            ],
        )
        print(f"Updated {len(checkouts_for_update)} trees in TreeListing", flush=True)
