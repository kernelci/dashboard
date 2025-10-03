from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False  # Required for `CONCURRENTLY`

    dependencies = [
        ("kernelCI_app", "0005_add_checkouts_indexes"),
    ]

    # Using separate operations because the indexes were already created with kcidb
    # and we can only use `IF NOT EXISTS` with raw SQL; we then also need to tell Django
    # that the models have been updated with the indexes.
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS builds__timestamp"
                    " ON builds (_timestamp);",
                    reverse_sql="DROP INDEX IF EXISTS builds__timestamp;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS builds_architecture"
                    " ON builds (architecture);",
                    reverse_sql="DROP INDEX IF EXISTS builds_architecture;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS builds_compiler"
                    " ON builds (compiler);",
                    reverse_sql="DROP INDEX IF EXISTS builds_compiler;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS builds_config_name"
                    " ON builds (config_name);",
                    reverse_sql="DROP INDEX IF EXISTS builds_config_name;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS builds_origin"
                    " ON builds (origin);",
                    reverse_sql="DROP INDEX IF EXISTS builds_origin;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS builds_start_time"
                    " ON builds (start_time);",
                    reverse_sql="DROP INDEX IF EXISTS builds_start_time;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS builds_status"
                    " ON builds (status);",
                    reverse_sql="DROP INDEX IF EXISTS builds_status;",
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="builds",
                    index=models.Index(
                        fields=["field_timestamp"], name="builds__timestamp"
                    ),
                ),
                migrations.AddIndex(
                    model_name="builds",
                    index=models.Index(
                        fields=["architecture"], name="builds_architecture"
                    ),
                ),
                migrations.AddIndex(
                    model_name="builds",
                    index=models.Index(fields=["compiler"], name="builds_compiler"),
                ),
                migrations.AddIndex(
                    model_name="builds",
                    index=models.Index(
                        fields=["config_name"], name="builds_config_name"
                    ),
                ),
                migrations.AddIndex(
                    model_name="builds",
                    index=models.Index(fields=["origin"], name="builds_origin"),
                ),
                migrations.AddIndex(
                    model_name="builds",
                    index=models.Index(fields=["start_time"], name="builds_start_time"),
                ),
                migrations.AddIndex(
                    model_name="builds",
                    index=models.Index(fields=["status"], name="builds_status"),
                ),
            ],
        ),
    ]
