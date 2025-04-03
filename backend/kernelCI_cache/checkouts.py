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
        origin_field = origin if origin is not None else checkout["origin"]

        # TODO: When we add patchset_hash to the TreeView, it should be added here too
        lookup_fields = {
            "origin": origin_field,
            "tree_name": checkout["tree_name"],
            "git_commit_hash": checkout["git_commit_hash"],
            "git_repository_url": checkout["git_repository_url"],
            "git_repository_branch": checkout["git_repository_branch"],
        }

        update_fields = {
            "checkout_id": checkout["id"],
            "start_time": checkout["start_time"],
            "git_commit_tags": json.dumps(checkout["git_commit_tags"]),
            "origin_builds_finish_time": checkout["origin_builds_finish_time"],
            "origin_tests_finish_time": checkout["origin_tests_finish_time"],
            "pass_builds": checkout["pass_builds"],
            "fail_builds": checkout["fail_builds"],
            "done_builds": checkout["done_builds"],
            "miss_builds": checkout["miss_builds"],
            "skip_builds": checkout["skip_builds"],
            "error_builds": checkout["error_builds"],
            "null_builds": checkout["null_builds"],
            "pass_boots": checkout["pass_boots"],
            "fail_boots": checkout["fail_boots"],
            "done_boots": checkout["done_boots"],
            "miss_boots": checkout["miss_boots"],
            "skip_boots": checkout["skip_boots"],
            "error_boots": checkout["error_boots"],
            "null_boots": checkout["null_boots"],
            "pass_tests": checkout["pass_tests"],
            "fail_tests": checkout["fail_tests"],
            "done_tests": checkout["done_tests"],
            "miss_tests": checkout["miss_tests"],
            "skip_tests": checkout["skip_tests"],
            "error_tests": checkout["error_tests"],
            "null_tests": checkout["null_tests"],
            "unstable": checkout["unstable"],
        }

        create_fields = {
            **update_fields,
            "field_timestamp": get_current_timestamp_kcidb_format(),
        }

        CheckoutsCache.objects.using("cache").update_or_create(
            **lookup_fields, defaults=update_fields, create_defaults=create_fields
        )
