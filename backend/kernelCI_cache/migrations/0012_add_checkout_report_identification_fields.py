from django.db import connections, migrations, models
from kernelCI import settings

_TEMP_DEFAULT = "none"


def populate_checkout_fields(apps, schema_editor):
    """
    Updates checkouts in the NotificationsCheckout table for anyone that has
    a null branch or git_repository_url using the kcidb data.
    """
    # Get checkouts that need updating from notifications database
    notifications_connection = connections["notifications"]
    notifications_query = """
        SELECT
            id, checkout_id, git_repository_branch, git_repository_url, origin
        FROM
            notifications_checkout
        WHERE
            git_repository_branch = %(temp_default)s
            OR git_repository_url = %(temp_default)s
    """
    params = {"temp_default": _TEMP_DEFAULT}

    with notifications_connection.cursor() as cursor:
        cursor.execute(notifications_query, params)
        checkouts_to_update = cursor.fetchall()

    if not checkouts_to_update:
        return

    # Queries in kcidb for the missing data
    kcidb_connection = (
        connections["kcidb"] if settings.USE_DASHBOARD_DB else connections["default"]
    )

    checkout_ids = [checkout[1] for checkout in checkouts_to_update]
    placeholders = ",".join(["%s"] * len(checkout_ids))
    kcidb_query = f"""
        SELECT
            id, git_repository_branch, git_repository_url, origin
        FROM checkouts
        WHERE
            id IN ({placeholders})
            -- in theory, all checkouts from the notifications table have branch and url not null,
            -- but this condition is used just to really guarantee that it won't break
            AND git_repository_branch IS NOT NULL
            AND git_repository_url IS NOT NULL
    """
    kcidb_checkouts_data = {}
    with kcidb_connection.cursor() as cursor:
        cursor.execute(kcidb_query, checkout_ids)
        kcidb_checkouts_data = cursor.fetchall()

    # Updates the notification checkouts with the kcidb data
    kcidb_checkouts_data_map = {data[0]: data for data in kcidb_checkouts_data}
    checkouts_for_bulk_update: list[tuple[str, str, str, str]] = []
    for checkout in checkouts_to_update:
        notification_id = checkout[0]
        n_checkout_id = checkout[1]
        n_branch = checkout[2]
        n_url = checkout[3]
        if n_checkout_id in kcidb_checkouts_data_map:
            data = kcidb_checkouts_data_map[n_checkout_id]
            n_branch = data[1]
            n_url = data[2]
            n_origin = data[3]
            checkouts_for_bulk_update.append(
                (notification_id, n_branch, n_url, n_origin)
            )

    if checkouts_for_bulk_update:
        with notifications_connection.cursor() as cursor:
            for checkout in checkouts_for_bulk_update:
                notification_id = checkout[0]
                n_branch = checkout[1]
                n_url = checkout[2]
                n_origin = checkout[3]
                cursor.execute(
                    """
                    UPDATE notifications_checkout
                    SET git_repository_branch = %s, git_repository_url = %s, origin = %s
                    WHERE id = %s
                    """,
                    [n_branch, n_url, n_origin, notification_id],
                )


class Migration(migrations.Migration):

    dependencies = [
        ("kernelCI_cache", "0011_copy_data_from_cache_if_exists"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificationscheckout",
            name="git_repository_branch",
            field=models.TextField(default=_TEMP_DEFAULT),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="notificationscheckout",
            name="git_repository_url",
            field=models.TextField(default=_TEMP_DEFAULT),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="notificationscheckout",
            name="origin",
            field=models.TextField(default="maestro", null=True),
        ),
        migrations.AddField(
            model_name="notificationscheckout",
            name="path",
            field=models.TextField(null=True),
        ),
        migrations.RunPython(populate_checkout_fields, hints={"run_always": True}),
    ]
