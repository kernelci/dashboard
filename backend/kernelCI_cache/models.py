from django.db import models

from kernelCI_app.constants.general import DEFAULT_ORIGIN


class NotificationsCheckout(models.Model):
    notification_message_id = models.TextField()
    notification_sent = models.DateTimeField()
    checkout_id = models.TextField()
    git_repository_branch = models.TextField()
    git_repository_url = models.TextField()
    origin = models.TextField(null=True, default=DEFAULT_ORIGIN)
    path = models.TextField(null=True)  # A list[str] stored as a json-like string

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
