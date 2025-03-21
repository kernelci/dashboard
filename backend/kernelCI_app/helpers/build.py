import re
from typing import Optional

from kernelCI_app.helpers.environment import get_schema_version
from kernelCI_app.typeModels.databases import PASS_STATUS, FAIL_STATUS, NULL_STATUS


def build_status_map(status: Optional[bool | str]) -> str:
    if isinstance(status, str):
        return status
    status_map = {True: PASS_STATUS, False: FAIL_STATUS, None: NULL_STATUS}
    return status_map.get(status)


def valid_status_field() -> str:
    is_new_schema = get_schema_version() == "5"
    return "status" if is_new_schema else "valid"


VALID_COL_REGEX = re.compile(r"column \S*valid\S* does not exist")


def is_valid_does_not_exist_exception(e: Exception) -> bool:
    return bool(VALID_COL_REGEX.search(str(e)))
