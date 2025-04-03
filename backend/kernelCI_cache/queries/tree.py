from typing import Optional
from kernelCI_cache.models import CheckoutsCache
from datetime import timedelta
from django.utils.timezone import now


def get_cached_tree_listing_data(
    *,
    origin: str,
    interval_in_days: Optional[int] = None,
    min_age_in_days: Optional[int] = None,
):
    query = CheckoutsCache.objects.using("cache").filter(origin=origin)

    if interval_in_days is not None:
        max_start_time_threshold = now() - timedelta(days=interval_in_days)
        query = query.filter(start_time__gte=max_start_time_threshold)

    if min_age_in_days is not None:
        min_start_time_threshold = now() - timedelta(days=min_age_in_days)
        query = query.filter(start_time__lte=min_start_time_threshold)

    return query.values()
