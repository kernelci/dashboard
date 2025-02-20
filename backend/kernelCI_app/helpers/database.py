def dict_fetchall(cursor) -> list[dict]:
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    This has a performance cost so avoid using it in large unprocessed data.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
