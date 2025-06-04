from django.db import connection
from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.helpers.database import dict_fetchall

ORIGINS_QUERY_KEY = "origins_query"
ORIGINS_CACHE_TIMEOUT = 12 * 60 * 60  # 12 hours


def get_origins() -> list[dict[str, str]]:
    origins = get_query_cache(key=ORIGINS_QUERY_KEY)

    if origins is None:
        query = """
            SELECT
                DISTINCT C.ORIGIN AS origin,
                'checkouts' AS table
            FROM
                CHECKOUTS C
            """

        with connection.cursor() as cursor:
            cursor.execute(query)
            records = dict_fetchall(cursor=cursor)
            if records:
                set_query_cache(
                    key=ORIGINS_QUERY_KEY,
                    rows=records,
                    timeout=ORIGINS_CACHE_TIMEOUT,
                )
            return records

    return origins
