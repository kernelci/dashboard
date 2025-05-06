from django.db import models


class CheckoutsCache(models.Model):
    field_timestamp = models.DateTimeField(db_column="_timestamp")
    checkout_id = models.TextField()
    origin = models.TextField()
    tree_name = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    git_repository_branch = models.TextField(blank=True, null=True)
    git_repository_url = models.TextField(blank=True, null=True)
    git_commit_hash = models.TextField(blank=True, null=True)
    git_commit_name = models.TextField(blank=True, null=True)
    git_commit_tags = models.TextField(blank=True, null=True)
    origin_builds_finish_time = models.DateTimeField(blank=True, null=True)
    origin_tests_finish_time = models.DateTimeField(blank=True, null=True)

    pass_builds = models.IntegerField(default=0)
    fail_builds = models.IntegerField(default=0)
    done_builds = models.IntegerField(default=0)
    miss_builds = models.IntegerField(default=0)
    skip_builds = models.IntegerField(default=0)
    error_builds = models.IntegerField(default=0)
    null_builds = models.IntegerField(default=0)

    pass_boots = models.IntegerField(default=0)
    fail_boots = models.IntegerField(default=0)
    done_boots = models.IntegerField(default=0)
    miss_boots = models.IntegerField(default=0)
    skip_boots = models.IntegerField(default=0)
    error_boots = models.IntegerField(default=0)
    null_boots = models.IntegerField(default=0)

    pass_tests = models.IntegerField(default=0)
    fail_tests = models.IntegerField(default=0)
    done_tests = models.IntegerField(default=0)
    miss_tests = models.IntegerField(default=0)
    skip_tests = models.IntegerField(default=0)
    error_tests = models.IntegerField(default=0)
    null_tests = models.IntegerField(default=0)

    unstable = models.BooleanField(default=True)

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


class NotificationsCheckout(models.Model):
    notification_message_id = models.TextField()
    notification_sent = models.DateTimeField()
    checkout_id = (
        models.TextField()
    )  # Not necessarily unique, 1 checkout can have n notifications

    class Meta:
        db_table = "notifications_checkout"


class NotificationsIssue(models.Model):
    # It is possible to store only the basic info of an issue, if it has 0 notifications
    notification_message_id = models.TextField(null=True)
    notification_sent = models.DateTimeField(null=True)

    # Unique together such that an issue can have at most 1 notification.
    # If an issue shall have multiple notifications, then we should lift this constraint
    # and store the data for if an issue has notifications in another table
    issue_id = models.TextField()
    issue_version = models.IntegerField()
    issue_type = models.TextField(
        null=True
    )  # PossibleIssueType (build/boot/test) | None

    class Meta:
        db_table = "notifications_issue"
        unique_together = (("issue_id", "issue_version"),)
