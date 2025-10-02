import django.contrib.postgres.indexes
import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False  # Required for `CONCURRENTLY`

    dependencies = [
        ("kernelCI_app", "0006_add_builds_indexes"),
    ]

    # Using separate operations because the indexes were already created with kcidb
    # and we can only use `IF NOT EXISTS` with raw SQL; we then also need to tell Django
    # that the models have been updated with the indexes.
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS tests__timestamp"
                    " ON tests (_timestamp);",
                    reverse_sql="DROP INDEX IF EXISTS tests__timestamp;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS tests_environment_compatible"
                    " ON tests USING GIN (environment_compatible);",
                    reverse_sql="DROP INDEX IF EXISTS tests_environment_compatible;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS tests_origin"
                    " ON tests (origin);",
                    reverse_sql="DROP INDEX IF EXISTS tests_origin;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS tests_path"
                    " ON tests (path);",
                    reverse_sql="DROP INDEX IF EXISTS tests_path;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS tests_platform_idx"
                    " ON tests ((environment_misc ->> 'platform'));",
                    reverse_sql="DROP INDEX IF EXISTS tests_platform_idx;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS tests_start_time"
                    " ON tests (start_time);",
                    reverse_sql="DROP INDEX IF EXISTS tests_start_time;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS tests_status"
                    " ON tests (status);",
                    reverse_sql="DROP INDEX IF EXISTS tests_status;",
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="tests",
                    index=models.Index(
                        fields=["field_timestamp"], name="tests__timestamp"
                    ),
                ),
                migrations.AddIndex(
                    model_name="tests",
                    index=django.contrib.postgres.indexes.GinIndex(
                        fields=["environment_compatible"],
                        name="tests_environment_compatible",
                    ),
                ),
                migrations.AddIndex(
                    model_name="tests",
                    index=models.Index(fields=["origin"], name="tests_origin"),
                ),
                migrations.AddIndex(
                    model_name="tests",
                    index=models.Index(fields=["path"], name="tests_path"),
                ),
                migrations.AddIndex(
                    model_name="tests",
                    index=models.Index(
                        django.db.models.expressions.RawSQL(
                            "(environment_misc ->> 'platform')", []
                        ),
                        name="tests_platform_idx",
                    ),
                ),
                migrations.AddIndex(
                    model_name="tests",
                    index=models.Index(fields=["start_time"], name="tests_start_time"),
                ),
                migrations.AddIndex(
                    model_name="tests",
                    index=models.Index(fields=["status"], name="tests_status"),
                ),
            ],
        ),
    ]
