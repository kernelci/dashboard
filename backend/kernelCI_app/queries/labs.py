from django.db import connection

from kernelCI_app.cache import get_query_cache, set_query_cache


def get_lab_origins(*, interval_in_days: int) -> list[str]:
    cache_key = f"lab_origins_query_{interval_in_days}"
    cached = get_query_cache(key=cache_key)
    if cached is not None:
        return cached

    query = """
        SELECT DISTINCT origin
        FROM lab_daily
        WHERE day >= CURRENT_DATE - %(interval_in_days)s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, {"interval_in_days": interval_in_days})
        origins = [row[0] for row in cursor.fetchall() if row[0]]
        if origins:
            set_query_cache(key=cache_key, rows=origins)
        return origins


def get_lab_listing_data(
    *,
    origin: str,
    interval_in_days: int,
) -> list[tuple]:
    cache_key = "labListing"
    params = {"origin": origin, "interval_in_days": interval_in_days}

    rows = get_query_cache(cache_key, params)
    if rows is not None:
        return rows

    query = """
        SELECT
            bl.name AS lab_name,
            COALESCE(SUM(d.build_pass), 0) AS build_pass,
            COALESCE(SUM(d.build_failed), 0) AS build_fail,
            COALESCE(SUM(d.build_inc), 0) AS build_inc,
            COALESCE(SUM(d.boot_pass), 0) AS boot_pass,
            COALESCE(SUM(d.boot_failed), 0) AS boot_fail,
            COALESCE(SUM(d.boot_inc), 0) AS boot_inc,
            COALESCE(SUM(d.test_pass), 0) AS test_pass,
            COALESCE(SUM(d.test_failed), 0) AS test_fail,
            COALESCE(SUM(d.test_inc), 0) AS test_inc
        FROM lab_daily d
        JOIN labs bl ON d.lab_id = bl.id
        WHERE d.origin = %(origin)s
          AND d.day >= CURRENT_DATE - %(interval_in_days)s
        GROUP BY bl.name
        ORDER BY bl.name
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    set_query_cache(key=cache_key, params=params, rows=rows)
    return rows
