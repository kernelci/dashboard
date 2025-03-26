from django.core.cache import cache
from django.conf import settings

timeout = settings.CACHE_TIMEOUT
DISCORD_NOTIFICATION_COOLDOWN = 600

DISCORD_NOTIFICATION_KEY = "discord_notification"

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


def set_notification_cache(*, notification: str) -> None:
    notification_hash = hash(notification)
    hash_key = f"{DISCORD_NOTIFICATION_KEY}-{notification_hash}"
    return cache.set(hash_key, notification, DISCORD_NOTIFICATION_COOLDOWN)


def get_notification_cache(*, notification: str) -> str:
    notification_hash = hash(notification)
    hash_key = f"{DISCORD_NOTIFICATION_KEY}-{notification_hash}"
    return cache.get(hash_key)


def _add_to_lookup(cache_key, property_key, lookup):
    if property_key is None:
        return
    if lookup[property_key] is None:
        lookup[property_key] = set()
    lookup[property_key].append(cache_key)
