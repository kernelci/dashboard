from django.db import models


class CheckoutsCache(models.Model):
    field_timestamp = models.DateTimeField(db_column="_timestamp")
    origin = models.TextField()
    tree_name = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    git_repository_branch = models.TextField(blank=True, null=True)
    git_repository_url = models.TextField(blank=True, null=True)
    git_commit_hash = models.TextField(blank=True, null=True)
    git_commit_name = models.TextField(blank=True, null=True)
    git_commit_tags = models.TextField(blank=True, null=True)

    build_pass = models.IntegerField(default=0)
    build_fail = models.IntegerField(default=0)
    build_done = models.IntegerField(default=0)
    build_miss = models.IntegerField(default=0)
    build_skip = models.IntegerField(default=0)
    build_error = models.IntegerField(default=0)
    build_null = models.IntegerField(default=0)

    boot_pass = models.IntegerField(default=0)
    boot_fail = models.IntegerField(default=0)
    boot_done = models.IntegerField(default=0)
    boot_miss = models.IntegerField(default=0)
    boot_skip = models.IntegerField(default=0)
    boot_error = models.IntegerField(default=0)
    boot_null = models.IntegerField(default=0)

    test_pass = models.IntegerField(default=0)
    test_fail = models.IntegerField(default=0)
    test_done = models.IntegerField(default=0)
    test_miss = models.IntegerField(default=0)
    test_skip = models.IntegerField(default=0)
    test_error = models.IntegerField(default=0)
    test_null = models.IntegerField(default=0)

    class Meta:
        db_table = "checkouts_cache"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "origin",
                    "tree_name",
                    "git_commit_hash",
                    "git_repository_url",
                    "git_repository_branch",
                ],
                name="unique_checkout",
            )
        ]
