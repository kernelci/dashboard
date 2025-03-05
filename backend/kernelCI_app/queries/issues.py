import os
from django.db.utils import ProgrammingError
from kernelCI_app.helpers.logger import log_message
import typing_extensions
from typing import Optional
from kernelCI_app.models import Incidents
from kernelCI_app.helpers.build import valid_do_not_exist_exception, valid_status_field
from kernelCI_app.constants.general import SCHEMA_VERSION_ENV


@typing_extensions.deprecated(
    "This implementation is temporary while the schema is being updated."
)
def get_issue_builds(*, issue_id: str, version: int) -> Optional[dict]:
    fields = [
        "build__id",
        "build__architecture",
        "build__config_name",
        f"build__{valid_status_field()}",
        "build__start_time",
        "build__duration",
        "build__compiler",
        "build__log_url",
        "build__checkout__tree_name",
        "build__checkout__git_repository_branch",
    ]

    try:
        return Incidents.objects.filter(
            issue_id=issue_id, issue_version=version
        ).values(*fields)
    except ProgrammingError as e:
        if valid_do_not_exist_exception(e):
            os.environ[SCHEMA_VERSION_ENV] = "5"
            log_message("Issue Builds -- Schema version updated to 5")
        else:
            raise
