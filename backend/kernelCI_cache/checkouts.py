import json
from kernelCI_app.typeModels.databases import Origin
from kernelCI_cache.models import CheckoutsCache
from kernelCI_cache.utils import get_current_timestamp_kcidb_format


# This function could be called from another thread if we face
# delays with endpoints in the future
def populate_checkouts_cache_db(data: list[dict], origin: Origin) -> None:
    for checkout in data:
        tree_name = (
            checkout["tree_names"][0] if len(checkout["tree_names"]) >= 1 else ""
        )

        # TODO: When we add patchset_hash to the TreeView, it should be added here too
        lookup_fields = {
            "origin": origin,
            "tree_name": tree_name,
            "git_commit_hash": checkout["git_commit_hash"],
            "git_repository_url": checkout["git_repository_url"],
            "git_repository_branch": checkout["git_repository_branch"],
        }

        update_fields = {
            "start_time": checkout["start_time"],
            "git_commit_tags": json.dumps(checkout["git_commit_tags"]),
            "build_pass": checkout["build_status"]["PASS"],
            "build_fail": checkout["build_status"]["FAIL"],
            "build_done": checkout["build_status"]["DONE"],
            "build_miss": checkout["build_status"]["MISS"],
            "build_skip": checkout["build_status"]["SKIP"],
            "build_error": checkout["build_status"]["ERROR"],
            "build_null": checkout["build_status"]["NULL"],
            "boot_pass": checkout["boot_status"]["pass"],
            "boot_fail": checkout["boot_status"]["fail"],
            "boot_done": checkout["boot_status"]["done"],
            "boot_miss": checkout["boot_status"]["miss"],
            "boot_skip": checkout["boot_status"]["skip"],
            "boot_error": checkout["boot_status"]["error"],
            "boot_null": checkout["boot_status"]["null"],
            "test_pass": checkout["test_status"]["pass"],
            "test_fail": checkout["test_status"]["fail"],
            "test_done": checkout["test_status"]["done"],
            "test_miss": checkout["test_status"]["miss"],
            "test_skip": checkout["test_status"]["skip"],
            "test_error": checkout["test_status"]["error"],
            "test_null": checkout["test_status"]["null"],
        }

        create_fields = {
            **update_fields,
            "field_timestamp": get_current_timestamp_kcidb_format(),
        }

        CheckoutsCache.objects.using("cache").update_or_create(
            **lookup_fields, defaults=update_fields, create_defaults=create_fields
        )
