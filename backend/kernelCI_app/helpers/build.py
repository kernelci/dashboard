import re
import os
import typing_extensions
from typing import Optional

from kernelCI_app.constants.general import SCHEMA_VERSION_ENV
from kernelCI_app.typeModels.databases import PASS_STATUS, FAIL_STATUS, NULL_STATUS


def build_status_map(status: Optional[bool | str]) -> str:
    if isinstance(status, str):
        return status
    status_map = {True: PASS_STATUS, False: FAIL_STATUS, None: NULL_STATUS}
    return status_map.get(status)


@typing_extensions.deprecated(
    "This implementation is temporary while the schema is being updated."
)
def valid_status_field() -> str:
    is_new_schema = os.getenv(SCHEMA_VERSION_ENV, "4") == "5"
    return "status" if is_new_schema else "valid"


VALID_COL_REGEX = re.compile(r"column \S*valid\S* does not exist")


@typing_extensions.deprecated(
    "This implementation is temporary while the schema is being updated."
)
def valid_do_not_exist_exception(e: Exception) -> bool:
    return bool(VALID_COL_REGEX.search(str(e)))
