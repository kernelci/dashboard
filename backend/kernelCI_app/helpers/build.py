import os

build_status_map = {True: "valid", False: "invalid", None: "null"}


def map_valid_status_field(field: str) -> str:
    is_new_schema = os.getenv("SCHEMA_VERSION", "4") == "5"
    return "status" if is_new_schema else "valid"
