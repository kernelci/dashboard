from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db.models import F, Q
from django.db.models.functions import Concat, MD5
from django.db.models.expressions import RawSQL


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
        indexes = [
            models.Index(fields=["field_timestamp"], name="issues__timestamp"),
            GinIndex(fields=["categories"], name="issues_categories"),
            models.Index(fields=["culprit_code"], name="issues_culprit_code"),
            models.Index(fields=["culprit_harness"], name="issues_culprit_harness"),
            models.Index(fields=["culprit_tool"], name="issues_culprit_tool"),
            models.Index(fields=["origin"], name="issues_origin"),
        ]


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
        indexes = [
            models.Index(fields=["field_timestamp"], name="checkouts__timestamp"),
            models.Index(fields=["git_commit_hash"], name="checkouts_commit_hash"),
            models.Index(fields=["git_commit_name"], name="checkouts_commit_name"),
            GinIndex(fields=["git_commit_tags"], name="checkouts_commit_tags"),
            models.Index(fields=["git_repository_branch"], name="checkouts_git_branch"),
            models.Index(fields=["git_repository_url"], name="checkouts_git_url"),
            models.Index(fields=["origin"], name="checkouts_origin"),
            models.Index(fields=["start_time"], name="checkouts_start_time"),
            models.Index(fields=["tree_name"], name="checkouts_tree_name"),
        ]


class Builds(models.Model):
    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    checkout = models.ForeignKey(
        Checkouts, db_constraint=False, on_delete=models.DO_NOTHING
    )
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
    series = models.GeneratedField(
        expression=MD5(
            Concat(
                F("config_name"),
                F("compiler"),
                F("architecture"),
            ),
        ),
        output_field=models.TextField(blank=True, null=True),
        db_persist=True,
    )

    class Meta:
        db_table = "builds"
        indexes = [
            models.Index(fields=["field_timestamp"], name="builds__timestamp"),
            models.Index(fields=["architecture"], name="builds_architecture"),
            models.Index(fields=["compiler"], name="builds_compiler"),
            models.Index(fields=["config_name"], name="builds_config_name"),
            models.Index(fields=["origin"], name="builds_origin"),
            models.Index(fields=["start_time"], name="builds_start_time"),
            models.Index(fields=["series"], name="builds_series_idx"),
            models.Index(fields=["status"], name="builds_status"),
        ]


class Tests(models.Model):
    class UnitPrefix(models.TextChoices):
        METRIC = "metric"
        BINARY = "binary"

    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    build = models.ForeignKey(Builds, db_constraint=False, on_delete=models.DO_NOTHING)
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
        indexes = [
            models.Index(fields=["field_timestamp"], name="tests__timestamp"),
            GinIndex(
                fields=["environment_compatible"], name="tests_environment_compatible"
            ),
            models.Index(fields=["origin"], name="tests_origin"),
            models.Index(fields=["path"], name="tests_path"),
            models.Index(
                RawSQL("(environment_misc ->> 'platform')", []),
                name="tests_platform_idx",
            ),
            models.Index(fields=["start_time"], name="tests_start_time"),
            models.Index(fields=["status"], name="tests_status"),
            # IMPORTANT: the next index is defined with where `environment_misc -> 'platform' IS NOT NULL`
            # This is not the desired behavior, it should be where
            # `environment_misc ->> 'platform' IS NOT NULL`, attention to the `->>`.
            # However Django doesn't seem to allow this format in a `condition` (Q) parameter. And we
            # must use `condition` since we are using the `fields` param as well. See PostgreSQL note on:
            # https://docs.djangoproject.com/en/5.2/topics/db/queries/#module-django.db.models.fields.json
            #
            # The fix is that in the migration we create the right condition separately, using raw sql.
            # *Check the migration for when this was added*.
            models.Index(
                fields=["origin", "start_time"],
                condition=Q(environment_misc__platform__isnull=False),
                name="tests_origin_time_platform",
            ),
        ]


class Incidents(models.Model):
    field_timestamp = models.DateTimeField(
        db_column="_timestamp", blank=True, null=True
    )
    id = models.TextField(primary_key=True)
    origin = models.TextField()
    issue = models.ForeignKey(Issues, db_constraint=False, on_delete=models.DO_NOTHING)
    issue_version = models.IntegerField()
    build = models.ForeignKey(
        Builds, db_constraint=False, null=True, blank=True, on_delete=models.DO_NOTHING
    )
    test = models.ForeignKey(
        Tests, db_constraint=False, null=True, blank=True, on_delete=models.DO_NOTHING
    )
    present = models.BooleanField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    misc = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "incidents"
        indexes = [
            models.Index(fields=["field_timestamp"], name="incidents__timestamp"),
            # Since there is no such thing as a composite foreign key, there is no automatic index on
            # (issue_id, issue_version). But since the issue_id alone is defined as an FK, there is
            # an automatic index on it. So we just need to add an index on issue_version alone.
            models.Index(fields=["issue_version"], name="incidents_issue_version"),
            models.Index(fields=["origin"], name="incidents_origin"),
        ]


class HardwareStatus(models.Model):
    hardware_origin = models.CharField(max_length=100)
    hardware_platform = models.CharField(max_length=100)
    compatibles = ArrayField(models.TextField(), null=True)
    date = models.IntegerField()

    build_pass = models.IntegerField()
    build_failed = models.IntegerField()
    build_inc = models.IntegerField()
    boot_pass = models.IntegerField()
    boot_failed = models.IntegerField()
    boot_inc = models.IntegerField()
    test_pass = models.IntegerField()
    test_failed = models.IntegerField()
    test_inc = models.IntegerField()

    class Meta:
        db_table = "hardware_status"
        unique_together = ("hardware_origin", "hardware_platform", "date")


class NewBuild(models.Model):
    build_id = models.TextField(primary_key=True)
    checkout_id = models.TextField()
    build_origin = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, blank=True, null=True
    )

    class Meta:
        db_table = "new_build"
        unique_together = ("build_id", "checkout_id")


class NewTest(models.Model):
    test_id = models.TextField(primary_key=True)
    build_id = models.TextField()
    test_origin = models.CharField(max_length=100)
    test_platform = models.CharField(max_length=100)
    test_compatible = ArrayField(models.TextField(), null=True)
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, blank=True, null=True
    )
    start_time = models.IntegerField()
    is_boot = models.BooleanField(default=False)

    class Meta:
        db_table = "new_test"
        unique_together = ("test_id", "build_id")


class BuildStatusByHardware(models.Model):
    hardware_origin = models.CharField(max_length=100)
    hardware_platform = models.CharField(max_length=100)
    build_id = models.TextField()

    class Meta:
        db_table = "build_status_by_hardware"
        unique_together = ("hardware_origin", "hardware_platform", "build_id")
