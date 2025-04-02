import json
from typing import Optional
from kernelCI_app.typeModels.databases import Origin
from kernelCI_cache.models import CheckoutsCache
from kernelCI_cache.utils import get_current_timestamp_kcidb_format


# This function could be called from another thread if we face
# delays with endpoints in the future
def populate_checkouts_cache_db(
    *,
    data: list[dict],
    origin: Optional[Origin] = None,
) -> None:
    for checkout in data:
        tree_name = (
            checkout["tree_names"][0] if len(checkout["tree_names"]) >= 1 else ""
        )
        origin_field = origin if origin is not None else checkout["origin"]

        # TODO: When we add patchset_hash to the TreeView, it should be added here too
        lookup_fields = {
            "origin": origin_field,
            "tree_name": tree_name,
            "git_commit_hash": checkout["git_commit_hash"],
            "git_repository_url": checkout["git_repository_url"],
            "git_repository_branch": checkout["git_repository_branch"],
        }

        update_fields = {
            "checkout_id": checkout["id"],
            "start_time": checkout["start_time"],
            "git_commit_tags": json.dumps(checkout["git_commit_tags"]),
            "build_pass": checkout["pass_builds"],
            "build_fail": checkout["fail_builds"],
            "build_done": checkout["done_builds"],
            "build_miss": checkout["miss_builds"],
            "build_skip": checkout["skip_builds"],
            "build_error": checkout["error_builds"],
            "build_null": checkout["null_builds"],
            "boot_pass": checkout["pass_boots"],
            "boot_fail": checkout["fail_boots"],
            "boot_done": checkout["done_boots"],
            "boot_miss": checkout["miss_boots"],
            "boot_skip": checkout["skip_boots"],
            "boot_error": checkout["error_boots"],
            "boot_null": checkout["null_boots"],
            "test_pass": checkout["pass_tests"],
            "test_fail": checkout["fail_tests"],
            "test_done": checkout["done_tests"],
            "test_miss": checkout["miss_tests"],
            "test_skip": checkout["skip_tests"],
            "test_error": checkout["error_tests"],
            "test_null": checkout["null_tests"],
            "unstable": checkout["unstable"],
        }

        create_fields = {
            **update_fields,
            "field_timestamp": get_current_timestamp_kcidb_format(),
        }

        CheckoutsCache.objects.using("cache").update_or_create(
            **lookup_fields, defaults=update_fields, create_defaults=create_fields
        )
