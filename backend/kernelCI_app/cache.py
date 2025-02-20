from django.core.cache import cache
from django.db import connection
from threading import Thread
from django.conf import settings

NOTIFY_CHANNEL = "teste"
timeout = settings.CACHE_TIMEOUT

__commit_lookup = {}
__build_lookup = {}
__test_lookup = {}


def __createCacheParamsHash(params: dict):
    params_list = list(params.items())
    params_list.sort(key=lambda x: x[0])
    params_string = ",".join([str(i[1]) for i in params_list])
    return hash(params_string)


def setQueryCache(
    key, params, rows, commit_hash=None, build_id=None, test_id=None, timeout=timeout
):
    params_hash = __createCacheParamsHash(params)
    hash_key = "%s-%s" % (key, params_hash)

    __addToLookup(hash_key, commit_hash, __commit_lookup)
    __addToLookup(hash_key, build_id, __build_lookup)
    __addToLookup(hash_key, test_id, __test_lookup)

    return cache.set(hash_key, rows, timeout)


def getQueryCache(key, params: dict):
    params_hash = __createCacheParamsHash(params)
    return cache.get("%s-%s" % (key, params_hash))


def runCacheInvalidator():
    cacheWorker = Thread(target=__listenWorker)
    cacheWorker.start()


def __invalidateCommit(commit):
    if commit in __commit_lookup:
        cache.delete_many(__commit_lookup[commit])


def __invalidateBuild(commit):
    if commit in __build_lookup:
        cache.delete_many(__build_lookup[commit])


def __invalidateTest(commit):
    if commit in __test_lookup:
        cache.delete_many(__test_lookup[commit])


def __processUpdate(value: str):
    if value.startswith("commit:"):
        __invalidateCommit(value.split(":", maxsplit=2)[1])
    elif value.startswith("build:"):
        __invalidateBuild(value.split(":", maxsplit=2)[1])
    elif value.startswith("test:"):
        __invalidateTest(value.split(":", maxsplit=2)[1])


def __listenWorker():
    try:
        with connection.cursor() as c:
            c.execute("LISTEN %s" % NOTIFY_CHANNEL)
            for n in c.connection.notifies():
                if n.channel == NOTIFY_CHANNEL:
                    __processUpdate(n.payload)
    except Exception as ex:
        print(ex)


def __addToLookup(cacheKey, propertyKey, lookup):
    if propertyKey is None:
        return
    if lookup[propertyKey] is None:
        lookup[propertyKey] = set()
    lookup[propertyKey].append(cacheKey)
