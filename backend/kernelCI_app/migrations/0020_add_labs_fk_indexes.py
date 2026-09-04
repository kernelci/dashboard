from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False  # Required for `CONCURRENTLY`

    dependencies = [
        ("kernelCI_app", "0019_labs_builds_lab_tests_lab"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS builds_lab_id"
                    " ON builds (lab_id);",
                    reverse_sql="DROP INDEX IF EXISTS builds_lab_id;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS tests_lab_id"
                    " ON tests (lab_id);",
                    reverse_sql="DROP INDEX IF EXISTS tests_lab_id;",
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="builds",
                    index=models.Index(fields=["lab"], name="builds_lab_id"),
                ),
                migrations.AddIndex(
                    model_name="tests",
                    index=models.Index(fields=["lab"], name="tests_lab_id"),
                ),
            ],
        ),
    ]
