from typing import Optional
from datetime import timedelta
from django.utils.timezone import now
from django.db import connections

from kernelCI_app.helpers.database import dict_fetchall


def get_cached_tree_listing_data(
    *,
    origin: str,
    interval_in_days: int = None,
    min_age_in_days: Optional[int] = None,
) -> list[dict]:
    params = {
        "origin": origin,
        "max_start_time": now() - timedelta(days=interval_in_days),
    }

    min_age_filter_clause = ""
    if min_age_in_days is not None:
        min_start_time_threshold = now() - timedelta(days=min_age_in_days)
        min_age_filter_clause = "AND start_time <= %(min_start_time)s"
        params["min_start_time"] = min_start_time_threshold

    # SQLite doesn't support DISTINCT ON, so we use ROW_NUMBER() instead
    query = f"""
        SELECT
            *
        FROM (
            SELECT
                c.*,
                ROW_NUMBER() OVER (
                    PARTITION BY c.git_repository_branch, c.git_repository_url
                    ORDER BY c.start_time DESC
                ) AS rn
            FROM
                checkouts_cache c
            WHERE
                origin = %(origin)s
                AND start_time >= %(max_start_time)s
                {min_age_filter_clause}
        ) WHERE
            rn = 1
    """

    with connections["cache"].cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)
