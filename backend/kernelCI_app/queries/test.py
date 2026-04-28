from typing import Optional

from django.db import connection, transaction

from kernelCI_app.cache import get_query_cache, set_query_cache
from kernelCI_app.helpers.database import dict_fetchall
from kernelCI_app.typeModels.databases import (
    Origin,
    Test__StartTime,
    Timestamp,
)


def get_test_details_data(*, test_id: str) -> list[dict]:
    params = {"test_id": test_id}

    query = """
    SELECT
        T._TIMESTAMP,
        T.ID,
        T.BUILD_ID,
        T.STATUS,
        T.PATH,
        T.LOG_EXCERPT,
        T.LOG_URL,
        T.MISC,
        T.ENVIRONMENT_MISC,
        T.START_TIME,
        T.ENVIRONMENT_COMPATIBLE,
        T.OUTPUT_FILES,
        T.INPUT_FILES,
        T.ORIGIN AS TEST_ORIGIN,
        B.COMPILER,
        B.ARCHITECTURE,
        B.CONFIG_NAME,
        C.GIT_COMMIT_HASH,
        C.GIT_REPOSITORY_BRANCH,
        C.GIT_REPOSITORY_URL,
        C.GIT_COMMIT_TAGS,
        C.TREE_NAME,
        C.ORIGIN
    FROM
        TESTS T
        LEFT JOIN BUILDS B ON T.BUILD_ID = B.ID
        LEFT JOIN CHECKOUTS C ON B.CHECKOUT_ID = C.ID
    WHERE
        T.ID = %(test_id)s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return dict_fetchall(cursor)


def get_test_status_history(
    *,
    path: str,
    origin: Origin,
    git_repository_url: str,
    git_repository_branch: str,
    platform: Optional[str],
    test_start_time: Test__StartTime,
    config_name: str,
    field_timestamp: Timestamp,
    group_size: int,
):
    cache_key = "TestStatusHistory"
    params = {
        "path": path,
        "origin": origin,
        "git_repository_url": git_repository_url,
        "git_repository_branch": git_repository_branch,
        "config_name": config_name,
        "group_size": group_size,
        "field_timestamp": field_timestamp,
        "platform": platform,
        "test_start_time": test_start_time,
    }

    if rows := get_query_cache(key=cache_key, params=params):
        return rows

    if platform is None:
        platform_clause = "AND T.ENVIRONMENT_MISC ->> 'platform' IS NULL"
    else:
        platform_clause = "AND T.ENVIRONMENT_MISC ->> 'platform' = %(platform)s"

    if test_start_time is None:
        if field_timestamp is None:
            time_clause = "AND T.START_TIME IS NULL AND T._TIMESTAMP IS NULL"
            order_clause = "ORDER BY T._TIMESTAMP DESC"
        else:
            time_clause = "AND T._TIMESTAMP <= %(field_timestamp)s"
            order_clause = "ORDER BY T._TIMESTAMP DESC"
    else:
        time_clause = "AND T.START_TIME <= %(test_start_time)s"
        order_clause = "ORDER BY T.START_TIME DESC"

    query = f"""
        SELECT
            T.START_TIME,
            T.ID,
            COALESCE(T.STATUS, 'NULL') AS status,
            C.GIT_COMMIT_HASH AS build__checkout__git_commit_hash
        FROM
            TESTS T
        INNER JOIN BUILDS B ON T.BUILD_ID = B.ID
        INNER JOIN CHECKOUTS C ON B.CHECKOUT_ID = C.ID
        WHERE
            T.PATH = %(path)s
            AND C.ORIGIN = %(origin)s
            AND C.GIT_REPOSITORY_URL = %(git_repository_url)s
            AND C.GIT_REPOSITORY_BRANCH = %(git_repository_branch)s
            AND B.CONFIG_NAME = %(config_name)s
            {platform_clause}
            {time_clause}
        {order_clause}
        LIMIT %(group_size)s;
    """

    with transaction.atomic():
        with connection.cursor() as cursor:
            # do not let postgres planner use a slow nested loop in the query
            # a hashed approach should always be faster here
            cursor.execute("SET LOCAL enable_nestloop = off")
            cursor.execute(query, params)
            rows = dict_fetchall(cursor)
            set_query_cache(key=cache_key, params=params, rows=rows)
            return rows
