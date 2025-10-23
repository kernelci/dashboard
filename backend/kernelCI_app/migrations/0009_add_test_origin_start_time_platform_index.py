from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False  # Required for `CONCURRENTLY`

    dependencies = [
        ("kernelCI_app", "0008_add_incidents_indexes"),
    ]

    operations = [
        # Rename existing index so that we can reuse it.
        # The existing index exceeds the maximum index name length for django (30 chars).
        migrations.RunSQL(
            "ALTER INDEX IF EXISTS tests_origin_start_time_platform_idx RENAME TO tests_origin_time_platform;"
        ),
        # Using separate operations because the indexes were already created with kcidb
        # and we can only use `IF NOT EXISTS` with raw SQL; we then also need to tell Django
        # that the models have been updated with the indexes.
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS tests_origin_time_platform"
                    " ON tests (origin, start_time) WHERE (environment_misc ->> 'platform') IS NOT NULL;",
                    reverse_sql="DROP INDEX IF EXISTS tests_origin_time_platform;",
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="tests",
                    index=models.Index(
                        condition=models.Q(
                            ("environment_misc__platform__isnull", False)
                        ),
                        fields=["origin", "start_time"],
                        name="tests_origin_time_platform",
                    ),
                ),
            ],
        ),
    ]
