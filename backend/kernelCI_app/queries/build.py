import os
from django.db.utils import ProgrammingError
import typing_extensions
from typing import Optional
from querybuilder.query import Query
from kernelCI_app.models import Builds, Tests
from kernelCI_app.helpers.build import valid_do_not_exist_exception, valid_status_field
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.constants.general import SCHEMA_VERSION_ENV


@typing_extensions.deprecated(
    "This implementation is temporary while the schema is being updated."
)
def get_build_details(build_id: str) -> Optional[list[dict]]:
    build_fields = [
        "id",
        "_timestamp",
        "checkout_id",
        "origin",
        "comment",
        "start_time",
        "log_excerpt",
        "duration",
        "architecture",
        "command",
        "compiler",
        "config_name",
        "config_url",
        "log_url",
        {"valid": valid_status_field()},
        "misc",
        "input_files",
        "output_files",
    ]

    query = Query().from_table(Builds, build_fields)
    query.join(
        "checkouts",
        join_type="LEFT JOIN",
        fields=[
            "tree_name",
            "git_repository_branch",
            "git_commit_name",
            "git_repository_url",
            "git_commit_hash",
            "git_commit_tags",
        ],
        condition="checkouts.id = builds.checkout_id",
    )
    query.where(**{"builds.id__eq": build_id})

    try:
        return query.select()
    except ProgrammingError as e:
        if valid_do_not_exist_exception(e):
            os.environ[SCHEMA_VERSION_ENV] = "5"
            log_message("Build Details -- Schema version updated to 5")
        else:
            raise


@typing_extensions.deprecated(
    "This implementation is temporary while the schema is being updated."
)
def get_build_tests(build_id: str) -> Optional[list[dict]]:
    try:
        result = Tests.objects.filter(build_id=build_id).values(
            "id",
            "duration",
            "status",
            "path",
            "start_time",
            "environment_compatible",
            "environment_misc",
            f"build__{valid_status_field()}",
        )
        return result
    except ProgrammingError as e:
        if valid_do_not_exist_exception(e):
            os.environ[SCHEMA_VERSION_ENV] = "5"
            log_message("Build Details Tests -- Schema version updated to 5")
        else:
            raise
