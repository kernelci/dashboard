from django.db import models
from django.contrib.postgres.fields import ArrayField


class StatusChoices(models.TextChoices):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"
    MISS = "MISS"
    DONE = "DONE"


class Issues(models.Model):
    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    id = models.TextField(primary_key=True)
    version = models.IntegerField()  # version is also part of the primary key in kcidb
    origin = models.TextField()
    report_url = models.TextField(blank=True, null=True)
    report_subject = models.TextField(blank=True, null=True)
    culprit_code = models.BooleanField(blank=True, null=True)
    culprit_tool = models.BooleanField(blank=True, null=True)
    culprit_harness = models.BooleanField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)
    categories = ArrayField(models.TextField(), blank=True, null=True)

    class Meta:
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
    patchset_files = models.JSONField(blank=True, null=True)
    patchset_hash = models.TextField(blank=True, null=True)
    message_id = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    log_url = models.TextField(blank=True, null=True)
    log_excerpt = models.CharField(max_length=16384, blank=True, null=True)
    valid = models.BooleanField(blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)
    git_commit_message = models.TextField(blank=True, null=True)
    git_repository_branch_tip = models.BooleanField(blank=True, null=True)
    git_commit_tags = ArrayField(models.TextField(), blank=True, null=True)
    origin_builds_finish_time = models.DateTimeField(blank=True, null=True)
    origin_tests_finish_time = models.DateTimeField(blank=True, null=True)

    class Meta:
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
    misc = models.JSONField(blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, blank=True, null=True
    )

    class Meta:
        db_table = "builds"


class Tests(models.Model):
    class UnitPrefix(models.TextChoices):
        METRIC = "metric"
        BINARY = "binary"

    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    build = models.ForeignKey(Builds, on_delete=models.DO_NOTHING)
    id = models.TextField(primary_key=True)
    origin = models.TextField()
    environment_comment = models.TextField(blank=True, null=True)
    environment_misc = models.JSONField(blank=True, null=True)
    path = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    log_url = models.TextField(blank=True, null=True)
    log_excerpt = models.CharField(max_length=16384, blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, blank=True, null=True
    )
    start_time = models.DateTimeField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    output_files = models.JSONField(blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)
    number_value = models.FloatField(blank=True, null=True)
    environment_compatible = ArrayField(models.TextField(), blank=True, null=True)
    number_prefix = models.CharField(
        max_length=10, choices=UnitPrefix.choices, blank=True, null=True
    )
    number_unit = models.TextField(blank=True, null=True)
    input_files = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "tests"


class Incidents(models.Model):
    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    id = models.TextField(primary_key=True)
    origin = models.TextField()
    issue = models.ForeignKey(Issues, on_delete=models.DO_NOTHING)
    issue_version = models.IntegerField()
    build = models.ForeignKey(
        Builds, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    test = models.ForeignKey(Tests, on_delete=models.DO_NOTHING, null=True, blank=True)
    present = models.BooleanField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "incidents"
