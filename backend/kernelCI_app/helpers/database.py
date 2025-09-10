from django.conf import settings
from django.db import connections


def dict_fetchall(cursor) -> list[dict]:
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    This has a performance cost so avoid using it in large unprocessed data.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_kcidb_connection():
    """Return the KCIDB connection regardless of default alias.

    When USE_DASHBOARD_DB is True, the default database points to the
    dashboard DB and KCIDB is exposed as the "kcidb" alias. Otherwise,
    KCIDB is the default connection.
    """
    return (
        connections["kcidb"] if getattr(settings, "USE_DASHBOARD_DB", False) else connections["default"]
    )


def get_kcidb_alias() -> str:
    """Return the Django DB alias for KCIDB ("kcidb" or "default")."""
    return "kcidb" if getattr(settings, "USE_DASHBOARD_DB", False) else "default"
