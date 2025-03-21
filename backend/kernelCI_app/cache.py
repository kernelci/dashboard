import json
from time import strftime, gmtime
from kernelCI_app.typeModels.treeListing import Checkout
from kernelCI_app.models import CheckoutCache
from django.core.cache import cache
from django.conf import settings

timeout = settings.CACHE_TIMEOUT

_commit_lookup = {}
_build_lookup = {}
_test_lookup = {}


def _create_cache_params_hash(params: dict):
    params_list = list(params.items())
    params_list.sort(key=lambda x: x[0])
    params_string = ",".join([str(i[1]) for i in params_list])
    return hash(params_string)


def set_query_cache(
    key, params, rows, commit_hash=None, build_id=None, test_id=None, timeout=timeout
):
    params_hash = _create_cache_params_hash(params)
    hash_key = "%s-%s" % (key, params_hash)

    _add_to_lookup(hash_key, commit_hash, _commit_lookup)
    _add_to_lookup(hash_key, build_id, _build_lookup)
    _add_to_lookup(hash_key, test_id, _test_lookup)

    return cache.set(hash_key, rows, timeout)


def get_query_cache(key, params: dict):
    params_hash = _create_cache_params_hash(params)
    return cache.get("%s-%s" % (key, params_hash))


def _add_to_lookup(cache_key, property_key, lookup):
    if property_key is None:
        return
    if lookup[property_key] is None:
        lookup[property_key] = set()
    lookup[property_key].append(cache_key)


# TODO: Make another thread run this function to not stop the endpoints from running
def populate_cache_db(data: list[Checkout]) -> None:
    for checkout in data:
        origin = checkout["origin"]
        tree_name = checkout["tree_names"][0]
        git_commit_hash = checkout["git_commit_hash"]
        git_repository_url = checkout["git_repository_url"]
        git_repository_branch = checkout["git_repository_branch"]

        try:
            cache_data = CheckoutCache.objects.using("cache").get(
                origin=origin,
                tree_name=tree_name,
                git_commit_hash=git_commit_hash,
                git_repository_url=git_repository_url,
                git_repository_branch=git_repository_branch,
            )
            # Only for commit porpuses
            if cache_data:
                pass
            # TODO: Complete update portion
        except CheckoutCache.DoesNotExist:
            new_checkout = CheckoutCache(
                origin=origin,
                tree_name=tree_name,
                # TODO: Check if it's the same format used in kcidb
                field_timestamp=strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                start_time=data["start_time"],
                git_repository_branch=git_repository_branch,
                git_repository_url=git_repository_url,
                git_commit_hash=git_commit_hash,
                git_commit_name=data["git_commit_name"],
                git_commit_tags=json.dumps(data["git_commit_tags"]),
                build_pass=data["build_status"]["PASS"],
                build_fail=data["build_status"]["FAIL"],
                build_done=data["build_status"]["DONE"],
                build_miss=data["build_status"]["MISS"],
                build_skip=data["build_status"]["SKIP"],
                build_error=data["build_status"]["ERROR"],
                build_null=data["build_status"]["NULL"],
                boot_pass=data["boot_status"]["pass"],
                boot_fail=data["boot_status"]["fail"],
                boot_done=data["boot_status"]["done"],
                boot_miss=data["boot_status"]["miss"],
                boot_skip=data["boot_status"]["skip"],
                boot_error=data["boot_status"]["error"],
                boot_null=data["boot_status"]["null"],
                test_pass=data["test_status"]["pass"],
                test_fail=data["test_status"]["fail"],
                test_done=data["test_status"]["done"],
                test_miss=data["test_status"]["miss"],
                test_skip=data["test_status"]["skip"],
                test_error=data["test_status"]["error"],
                test_null=data["test_status"]["null"],
            )
            new_checkout.save(using="cache")
        except CheckoutCache.MultipleObjectsReturned:
            # We are assuming this shouldn't exist
            pass
