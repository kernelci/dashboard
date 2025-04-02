from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.models import Checkouts

ORIGINS_QUERY_KEY = "origins"
ORIGINS_CACHE_TIMEOUT = 12 * 60 * 60  # 12 hours


def get_origins() -> list[str]:
    origins = get_query_cache(key=ORIGINS_QUERY_KEY)
    if origins is None:
        origins = [
            checkout["origin"]
            for checkout in Checkouts.objects.values("origin").distinct()
        ]
        set_query_cache(
            key=ORIGINS_QUERY_KEY, rows=origins, timeout=ORIGINS_CACHE_TIMEOUT
        )
    return origins
