from django.db import models
from django.contrib.postgres.fields import ArrayField


class Issues(models.Model):
    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    id = models.TextField(primary_key=True)
    version = models.IntegerField()
    origin = models.TextField()
    report_url = models.TextField(blank=True, null=True)
    report_subject = models.TextField(blank=True, null=True)
    culprit_code = models.BooleanField(blank=True, null=True)
    culprit_tool = models.BooleanField(blank=True, null=True)
    culprit_harness = models.BooleanField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "issues"
        unique_together = (("id", "version"),)


class Checkouts(models.Model):
    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    id = models.TextField(primary_key=True)
    origin = models.TextField()
    tree_name = models.TextField(blank=True, null=True)
    git_repository_url = models.TextField(blank=True, null=True)
    git_commit_hash = models.TextField(blank=True, null=True)
    git_commit_name = models.TextField(blank=True, null=True)
    git_repository_branch = models.TextField(blank=True, null=True)
    git_commit_tags = ArrayField(models.TextField(), blank=True, null=True)
    patchset_files = models.JSONField(blank=True, null=True)
    patchset_hash = models.TextField(blank=True, null=True)
    message_id = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    log_url = models.TextField(blank=True, null=True)
    log_excerpt = models.CharField(max_length=16384, blank=True, null=True)
    valid = models.BooleanField(blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "checkouts"


class Builds(models.Model):
    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    checkout = models.ForeignKey(Checkouts, on_delete=models.DO_NOTHING)
    id = models.TextField(primary_key=True)
    origin = models.TextField()
    comment = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    architecture = models.TextField(blank=True, null=True)
    command = models.TextField(blank=True, null=True)
    compiler = models.TextField(blank=True, null=True)
    input_files = models.JSONField(blank=True, null=True)
    output_files = models.JSONField(blank=True, null=True)
    config_name = models.TextField(blank=True, null=True)
    config_url = models.TextField(blank=True, null=True)
    log_url = models.TextField(blank=True, null=True)
    log_excerpt = models.CharField(max_length=16384, blank=True, null=True)
    valid = models.BooleanField(blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "builds"


class Tests(models.Model):
    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    build = models.ForeignKey(Builds, on_delete=models.DO_NOTHING)
    id = models.TextField(primary_key=True)
    origin = models.TextField()
    environment_comment = models.TextField(blank=True, null=True)
    environment_compatible = ArrayField(
        models.TextField(), blank=True, default=list, null=True
    )
    environment_misc = models.JSONField(blank=True, null=True)
    path = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    log_url = models.TextField(blank=True, null=True)
    log_excerpt = models.CharField(max_length=16384, blank=True, null=True)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    start_time = models.DateTimeField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    output_files = models.JSONField(blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "tests"


class Incidents(models.Model):
    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    id = models.TextField(primary_key=True)
    origin = models.TextField()
    issue = models.ForeignKey(Issues, on_delete=models.DO_NOTHING)
    issue_version = models.IntegerField()
    build = models.ForeignKey(Builds, on_delete=models.DO_NOTHING)
    test = models.ForeignKey(Tests, on_delete=models.DO_NOTHING)
    present = models.BooleanField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "incidents"
