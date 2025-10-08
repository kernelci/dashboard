import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False  # Required for `CONCURRENTLY`

    dependencies = [
        ("kernelCI_app", "0003_add_build_series_field"),
    ]

    # Using separate operations because the indexes were already created with kcidb
    # and we can only use `IF NOT EXISTS` with raw SQL; we then also need to tell Django
    # that the models have been updated with the indexes.
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS issues__timestamp"
                    " ON issues (_timestamp);",
                    reverse_sql="DROP INDEX IF EXISTS issues__timestamp;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS issues_categories"
                    " ON issues USING GIN (categories);",
                    reverse_sql="DROP INDEX IF EXISTS issues_categories;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS issues_culprit_code"
                    " ON issues (culprit_code);",
                    reverse_sql="DROP INDEX IF EXISTS issues_culprit_code;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS issues_culprit_harness"
                    " ON issues (culprit_harness);",
                    reverse_sql="DROP INDEX IF EXISTS issues_culprit_harness;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS issues_culprit_tool"
                    " ON issues (culprit_tool);",
                    reverse_sql="DROP INDEX IF EXISTS issues_culprit_tool;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS issues_origin"
                    " ON issues (origin);",
                    reverse_sql="DROP INDEX IF EXISTS issues_origin;",
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="issues",
                    index=models.Index(
                        fields=["field_timestamp"], name="issues__timestamp"
                    ),
                ),
                migrations.AddIndex(
                    model_name="issues",
                    index=django.contrib.postgres.indexes.GinIndex(
                        fields=["categories"], name="issues_categories"
                    ),
                ),
                migrations.AddIndex(
                    model_name="issues",
                    index=models.Index(
                        fields=["culprit_code"], name="issues_culprit_code"
                    ),
                ),
                migrations.AddIndex(
                    model_name="issues",
                    index=models.Index(
                        fields=["culprit_harness"], name="issues_culprit_harness"
                    ),
                ),
                migrations.AddIndex(
                    model_name="issues",
                    index=models.Index(
                        fields=["culprit_tool"], name="issues_culprit_tool"
                    ),
                ),
                migrations.AddIndex(
                    model_name="issues",
                    index=models.Index(fields=["origin"], name="issues_origin"),
                ),
            ],
        ),
    ]
