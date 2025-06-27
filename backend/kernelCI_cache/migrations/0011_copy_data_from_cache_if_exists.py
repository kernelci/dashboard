from kernelCI.settings import DATABASES
from kernelCI_app.helpers.discordWebhook import send_discord_notification
from django.db import migrations, connections

cache_path = DATABASES["cache"]["NAME"]


def _copy_if_data_not_exists(
    cache_cursor, notif_cursor, table_name: str, columns: list[str]
):
    notif_cursor.execute(f"""SELECT id FROM {table_name} LIMIT 1;""")
    existent_data = notif_cursor.fetchone()
    if not existent_data:
        print(f"Copying data from {table_name}")
        query_placeholder = ", ".join(["?"] * len(columns))
        columns_names = ", ".join(columns)
        cache_cursor.execute(
            f"""SELECT {columns_names}
            FROM {table_name};"""
        )
        rows = cache_cursor.fetchall()
        if rows:
            notif_cursor.executemany(
                f"""INSERT INTO {table_name}
                ({columns_names})
                VALUES ({query_placeholder})""",
                rows,
            )
    else:
        print(
            f"Skipping {table_name} migration: "
            f"Data already exists in the {table_name} table."
        )


def copy_from_cache_to_notification_tables(apps, schema_editor):
    cache_conn = connections["cache"]
    notification_conn = connections["notifications"]

    with cache_conn.cursor() as cache_cursor, notification_conn.cursor() as notif_cursor:
        try:
            print("\nRUNNING DATA TRANSFER MIGRATION")
            # Check if tables exist in databases
            cache_cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='notifications_checkout';"
            )
            has_checkout_cache = cache_cursor.fetchone() is not None

            cache_cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='notifications_issue';"
            )
            has_issue_cache = cache_cursor.fetchone() is not None

            notif_cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='notifications_checkout';"
            )
            has_checkout_notif = notif_cursor.fetchone() is not None

            notif_cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='notifications_issue';"
            )
            has_issue_notif = notif_cursor.fetchone() is not None

            try:
                # Copy data if both tables exist in both dbs and if the target tables are empty
                if has_checkout_cache and has_checkout_notif:
                    _copy_if_data_not_exists(
                        cache_cursor=cache_cursor,
                        notif_cursor=notif_cursor,
                        table_name="notifications_checkout",
                        columns=[
                            "id",
                            "notification_message_id",
                            "notification_sent",
                            "checkout_id",
                        ],
                    )
                else:
                    print(
                        "Skipping notifications_checkout migration: "
                        "Table does not exist in one of the databases."
                    )

                if has_issue_cache and has_issue_notif:
                    _copy_if_data_not_exists(
                        cache_cursor=cache_cursor,
                        notif_cursor=notif_cursor,
                        table_name="notifications_issue",
                        columns=[
                            "id",
                            "notification_message_id",
                            "notification_sent",
                            "issue_id",
                            "issue_version",
                            "issue_type",
                        ],
                    )
                else:
                    print(
                        "Skipping notifications_issue migration: "
                        "Table does not exist in one of the databases."
                    )
            except Exception as e:
                cache_cursor.rollback()
                notif_cursor.rollback()
                raise e
        except Exception as e:
            print(f"\nError during data transfer migration: {e}.")
            send_discord_notification(
                content=f"\nError during data transfer migration: {e}."
            )
            raise e


class Migration(migrations.Migration):

    dependencies = [
        ("kernelCI_cache", "0010_notificationsissue"),
    ]

    operations = [
        migrations.RunPython(
            copy_from_cache_to_notification_tables, hints={"run_always": True}
        ),
    ]
