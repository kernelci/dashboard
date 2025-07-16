from django.db import connection
from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.helpers.database import dict_fetchall

ORIGINS_CACHE_TIMEOUT = 12 * 60 * 60  # 12 hours


def get_origins(interval_in_days) -> list[dict[str, str]]:
    origins_query_key = f"origins_query_{interval_in_days}"
    origins = get_query_cache(key=origins_query_key)

    if origins is None:
        query = """
            SELECT
                DISTINCT C.ORIGIN AS origin,
                'checkouts' AS table
            FROM
                CHECKOUTS C
            WHERE
                C.start_time >= CURRENT_DATE - INTERVAL '%(interval_in_days)s days'
            """

        with connection.cursor() as cursor:
            cursor.execute(query, {"interval_in_days": interval_in_days})
            records = dict_fetchall(cursor=cursor)
            if records:
                set_query_cache(
                    key=origins_query_key,
                    rows=records,
                    timeout=ORIGINS_CACHE_TIMEOUT,
                )
            return records

    return origins
