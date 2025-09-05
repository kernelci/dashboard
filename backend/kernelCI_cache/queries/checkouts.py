from django.db import connections
from kernelCI_app.helpers.database import dict_fetchall


def get_cached_tree_listing_fast():
    """Returns the most recent checkout of the trees that are cached in the sqlite database"""

    query = """
        SELECT * FROM (
            SELECT
                checkout_id,
                tree_name,
                git_repository_branch,
                git_repository_url,
                start_time,
                unstable,
                ROW_NUMBER() OVER (
                    PARTITION BY
                        tree_name,
                        git_repository_branch,
                        git_repository_url
                    ORDER BY start_time DESC
                ) as rn
            FROM
                checkouts_cache
        ) WHERE rn = 1
    """

    with connections["cache"].cursor() as cursor:
        cursor.execute(query)
        records = dict_fetchall(cursor)

    return records
