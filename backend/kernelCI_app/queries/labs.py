from django.db import connection


def get_lab_listing_data(
    *,
    origin: str,
    interval_in_days: int,
) -> list[tuple]:
    params = {
        "origin": origin,
        "interval": f"{interval_in_days} days",
    }

    query = """
        WITH status_counts AS (
            SELECT
                COALESCE(bl.name, b.misc->>'lab') AS lab_name,
                'build' AS item_type,
                CASE
                    WHEN b.status IN ('PASS', 'FAIL') THEN b.status
                    ELSE 'INCONCLUSIVE'
                END AS item_status,
                COUNT(*) AS item_count
            FROM builds b
            LEFT JOIN labs bl ON b.lab_id = bl.id
            WHERE
                b.origin = %(origin)s
                AND b.start_time >= NOW() - INTERVAL %(interval)s
                AND b.id NOT LIKE 'maestro:dummy_%%'
                AND COALESCE(bl.name, b.misc->>'lab') IS NOT NULL
            GROUP BY 1, 2, 3

            UNION ALL

            SELECT
                COALESCE(tl.name, t.misc->>'runtime') AS lab_name,
                CASE
                    WHEN t.path = 'boot' OR t.path LIKE 'boot.%%' THEN 'boot'
                    ELSE 'test'
                END AS item_type,
                CASE
                    WHEN t.status IN ('PASS', 'FAIL') THEN t.status
                    ELSE 'INCONCLUSIVE'
                END AS item_status,
                COUNT(*) AS item_count
            FROM tests t
            LEFT JOIN labs tl ON t.lab_id = tl.id
            WHERE
                t.origin = %(origin)s
                AND t.start_time >= NOW() - INTERVAL %(interval)s
                AND t.path IS NOT NULL
                AND COALESCE(tl.name, t.misc->>'runtime') IS NOT NULL
            GROUP BY 1, 2, 3
        )
        SELECT
            lab_name,
            COALESCE(SUM(item_count) FILTER (
                WHERE item_type = 'build' AND item_status = 'PASS'
            ), 0) AS build_pass,
            COALESCE(SUM(item_count) FILTER (
                WHERE item_type = 'build' AND item_status = 'FAIL'
            ), 0) AS build_fail,
            COALESCE(SUM(item_count) FILTER (
                WHERE item_type = 'build' AND item_status = 'INCONCLUSIVE'
            ), 0) AS build_inc,
            COALESCE(SUM(item_count) FILTER (
                WHERE item_type = 'boot' AND item_status = 'PASS'
            ), 0) AS boot_pass,
            COALESCE(SUM(item_count) FILTER (
                WHERE item_type = 'boot' AND item_status = 'FAIL'
            ), 0) AS boot_fail,
            COALESCE(SUM(item_count) FILTER (
                WHERE item_type = 'boot' AND item_status = 'INCONCLUSIVE'
            ), 0) AS boot_inc,
            COALESCE(SUM(item_count) FILTER (
                WHERE item_type = 'test' AND item_status = 'PASS'
            ), 0) AS test_pass,
            COALESCE(SUM(item_count) FILTER (
                WHERE item_type = 'test' AND item_status = 'FAIL'
            ), 0) AS test_fail,
            COALESCE(SUM(item_count) FILTER (
                WHERE item_type = 'test' AND item_status = 'INCONCLUSIVE'
            ), 0) AS test_inc
        FROM status_counts
        GROUP BY lab_name
        ORDER BY lab_name
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()
