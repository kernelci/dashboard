from typing import Optional
import os
from pydantic import BaseModel


def build_status_map(status: Optional[bool | str]) -> str:
    if isinstance(status, str):
        return status.lower()
    status_map = {True: "pass", False: "fail", None: "null"}
    return status_map.get(status)


def field_build_status_map(model: BaseModel, alias: str) -> Optional[str]:
    return next(
        (field for field, info in model.__fields__.items() if info.alias == alias),
        None,
    )


def map_valid_status_field(field: str) -> str:
    is_new_schema = os.getenv("SCHEMA_VERSION", "4") == "5"
    return "status" if is_new_schema else "valid"
