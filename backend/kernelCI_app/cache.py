import gzip
import json
import pickle
from typing import Optional

from django.conf import settings
from django.core.cache import cache

from kernelCI_app.utils import stable_hash

timeout = settings.CACHE_TIMEOUT
DISCORD_NOTIFICATION_COOLDOWN = 600

DISCORD_NOTIFICATION_KEY = "discord_notification"

_commit_lookup = {}
_build_lookup = {}
_test_lookup = {}


def _create_cache_params_hash(params: dict) -> str:
    params_string = json.dumps(params, sort_keys=True, default=str)
    return stable_hash(params_string)


def _query_cache_key(key, params: Optional[dict] = None) -> str:
    if params is None:
        return key
    return "%s-%s" % (key, _create_cache_params_hash(params))


def _pack_query_cache(value):
    raw = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
    compressed = gzip.compress(raw)
    if len(compressed) < len(raw):
        return compressed
    return value


def _is_gzip(value) -> bool:
    # gzip header. _pack_query_cache is the only writer of bytes in this cache.
    return isinstance(value, bytes) and value.startswith(b"\x1f\x8b")


def _unpack_query_cache(value):
    if not _is_gzip(value):
        return value
    try:
        # Same trust as Django's Redis serializer: this process wrote the blob.
        return pickle.loads(gzip.decompress(value))  # noqa: S301
    except Exception:
        # A broken blob is a miss, so the query runs again.
        return None


def set_query_cache(
    *,
    key,
    params=None,
    rows,
    commit_hash=None,
    build_id=None,
    test_id=None,
    timeout=timeout,
    compress=False,
):
    hash_key = _query_cache_key(key, params)

    _add_to_lookup(hash_key, commit_hash, _commit_lookup)
    _add_to_lookup(hash_key, build_id, _build_lookup)
    _add_to_lookup(hash_key, test_id, _test_lookup)

    stored = _pack_query_cache(rows) if compress else rows
    return cache.set(hash_key, stored, timeout)


def get_query_cache(key, params: Optional[dict] = None):
    return _unpack_query_cache(cache.get(_query_cache_key(key, params)))


def clear_cache(key, params: Optional[dict] = None) -> None:
    if params is not None:
        cache.delete(_query_cache_key(key, params))
        return

    cache.delete(key)
    prefix = f"{key}-"
    version_mark = f":{cache.version}:"
    backend = cache._cache
    get_client = getattr(backend, "get_client", None)
    if get_client is not None:
        raw_keys = get_client().scan_iter(match=f"*{version_mark}{prefix}*", count=200)
    elif isinstance(backend, dict):
        raw_keys = list(backend)
    else:
        return

    names = []
    for raw_key in raw_keys:
        stored = raw_key.decode() if isinstance(raw_key, bytes) else raw_key
        logical = stored.split(version_mark, 1)[-1]
        if logical.startswith(prefix):
            names.append(logical)
    if names:
        cache.delete_many(names)


def set_notification_cache(*, notification: str) -> None:
    notification_hash = stable_hash(notification)
    hash_key = f"{DISCORD_NOTIFICATION_KEY}-{notification_hash}"
    return cache.set(hash_key, notification, DISCORD_NOTIFICATION_COOLDOWN)


def get_notification_cache(*, notification: str) -> str:
    notification_hash = stable_hash(notification)
    hash_key = f"{DISCORD_NOTIFICATION_KEY}-{notification_hash}"
    return cache.get(hash_key)


def _add_to_lookup(cache_key, property_key, lookup):
    if property_key is None:
        return

    lookup_property_key = lookup.get(property_key, set())
    lookup_property_key.add(cache_key)
    lookup[property_key] = lookup_property_key
