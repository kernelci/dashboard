def dict_fetchall(cursor) -> list[dict]:
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    This has a performance cost so avoid using it in large unprocessed data.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]


def debug_query(cursor, query, params) -> tuple[str, str]:
    sql = cursor.mogrify(query, params)
    profile = "\n".join(
        row for row, *_ in cursor.execute(f"EXPLAIN (ANALYZE, BUFFERS) {query}", params)
    )
    return (sql, profile)


def print_debug_query(cursor, query, params):
    print("{}\n{}\n".format(*debug_query(cursor, query, params)))
