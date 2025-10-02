from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False  # Required for `CONCURRENTLY`

    dependencies = [
        ("kernelCI_app", "0007_add_tests_indexes"),
    ]

    # Using separate operations because the indexes were already created with kcidb
    # and we can only use `IF NOT EXISTS` with raw SQL; we then also need to tell Django
    # that the models have been updated with the indexes.
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS incidents__timestamp"
                    " ON incidents (_timestamp);",
                    reverse_sql="DROP INDEX IF EXISTS incidents__timestamp;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS incidents_issue_version"
                    " ON incidents (issue_version);",
                    reverse_sql="DROP INDEX IF EXISTS incidents_issue_version;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS incidents_origin"
                    " ON incidents (origin);",
                    reverse_sql="DROP INDEX IF EXISTS incidents_origin;",
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="incidents",
                    index=models.Index(
                        fields=["field_timestamp"], name="incidents__timestamp"
                    ),
                ),
                migrations.AddIndex(
                    model_name="incidents",
                    index=models.Index(
                        fields=["issue_version"], name="incidents_issue_version"
                    ),
                ),
                migrations.AddIndex(
                    model_name="incidents",
                    index=models.Index(fields=["origin"], name="incidents_origin"),
                ),
            ],
        ),
    ]
