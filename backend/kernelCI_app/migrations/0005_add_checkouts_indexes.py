import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False  # Required for `CONCURRENTLY`

    dependencies = [
        ("kernelCI_app", "0004_add_issues_indexes"),
    ]

    # Using separate operations because the indexes were already created with kcidb
    # and we can only use `IF NOT EXISTS` with raw SQL; we then also need to tell Django
    # that the models have been updated with the indexes.
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS checkouts__timestamp"
                    " ON checkouts (_timestamp);",
                    reverse_sql="DROP INDEX IF EXISTS checkouts__timestamp;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS checkouts_commit_hash"
                    " ON checkouts (git_commit_hash);",
                    reverse_sql="DROP INDEX IF EXISTS checkouts_commit_hash;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS checkouts_commit_name"
                    " ON checkouts (git_commit_name);",
                    reverse_sql="DROP INDEX IF EXISTS checkouts_commit_name;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS checkouts_commit_tags"
                    " ON checkouts USING GIN (git_commit_tags);",
                    reverse_sql="DROP INDEX IF EXISTS checkouts_commit_tags;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS checkouts_git_branch"
                    " ON checkouts (git_repository_branch);",
                    reverse_sql="DROP INDEX IF EXISTS checkouts_git_branch;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS checkouts_git_url"
                    " ON checkouts (git_repository_url);",
                    reverse_sql="DROP INDEX IF EXISTS checkouts_git_url;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS checkouts_origin"
                    " ON checkouts (origin);",
                    reverse_sql="DROP INDEX IF EXISTS checkouts_origin;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS checkouts_start_time"
                    " ON checkouts (start_time);",
                    reverse_sql="DROP INDEX IF EXISTS checkouts_start_time;",
                ),
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS checkouts_tree_name"
                    " ON checkouts (tree_name);",
                    reverse_sql="DROP INDEX IF EXISTS checkouts_tree_name;",
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name="checkouts",
                    index=models.Index(
                        fields=["field_timestamp"], name="checkouts__timestamp"
                    ),
                ),
                migrations.AddIndex(
                    model_name="checkouts",
                    index=models.Index(
                        fields=["git_commit_hash"], name="checkouts_commit_hash"
                    ),
                ),
                migrations.AddIndex(
                    model_name="checkouts",
                    index=models.Index(
                        fields=["git_commit_name"], name="checkouts_commit_name"
                    ),
                ),
                migrations.AddIndex(
                    model_name="checkouts",
                    index=django.contrib.postgres.indexes.GinIndex(
                        fields=["git_commit_tags"], name="checkouts_commit_tags"
                    ),
                ),
                migrations.AddIndex(
                    model_name="checkouts",
                    index=models.Index(
                        fields=["git_repository_branch"], name="checkouts_git_branch"
                    ),
                ),
                migrations.AddIndex(
                    model_name="checkouts",
                    index=models.Index(
                        fields=["git_repository_url"], name="checkouts_git_url"
                    ),
                ),
                migrations.AddIndex(
                    model_name="checkouts",
                    index=models.Index(fields=["origin"], name="checkouts_origin"),
                ),
                migrations.AddIndex(
                    model_name="checkouts",
                    index=models.Index(
                        fields=["start_time"], name="checkouts_start_time"
                    ),
                ),
                migrations.AddIndex(
                    model_name="checkouts",
                    index=models.Index(
                        fields=["tree_name"], name="checkouts_tree_name"
                    ),
                ),
            ],
        ),
    ]
