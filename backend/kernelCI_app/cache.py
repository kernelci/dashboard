from django.core.cache import cache
from django.db import connection
from threading import Thread
from django.conf import settings

NOTIFY_CHANNEL = "teste"
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


def run_cache_invalidator():
    cache_worker = Thread(target=_listen_worker)
    cache_worker.start()


def _invalidate_commit(commit):
    if commit in _commit_lookup:
        cache.delete_many(_commit_lookup[commit])


def _invalidate_build(commit):
    if commit in _build_lookup:
        cache.delete_many(_build_lookup[commit])


def _invalidate_test(commit):
    if commit in _test_lookup:
        cache.delete_many(_test_lookup[commit])


def _process_update(value: str):
    if value.startswith("commit:"):
        _invalidate_commit(value.split(":", maxsplit=2)[1])
    elif value.startswith("build:"):
        _invalidate_build(value.split(":", maxsplit=2)[1])
    elif value.startswith("test:"):
        _invalidate_test(value.split(":", maxsplit=2)[1])


def _listen_worker():
    try:
        with connection.cursor() as c:
            c.execute("LISTEN %s" % NOTIFY_CHANNEL)
            for n in c.connection.notifies():
                if n.channel == NOTIFY_CHANNEL:
                    _process_update(n.payload)
    except Exception as ex:
        print(ex)


def _add_to_lookup(cache_key, property_key, lookup):
    if property_key is None:
        return
    if lookup[property_key] is None:
        lookup[property_key] = set()
    lookup[property_key].append(cache_key)
