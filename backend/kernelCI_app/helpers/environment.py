import yaml

from kernelCI_app.constants.general import (
    SCHEMA_VERSION_ENV_FILE,
    SCHEMA_VERSION_ENV_NAME,
)
from kernelCI_app.helpers.logger import log_message

DEFAULT_SCHEMA_VERSION = "5"


def get_yaml_data(*, file: str):
    try:
        with open(file, "r") as f:
            data = yaml.safe_load(f)
            return data
    except FileNotFoundError as e:
        log_message(f"File not found at {file}\n Error: {e}")
        return None
    except yaml.YAMLError as e:
        log_message(f"Error parsing YAML: {e}")
        return None


def set_yaml_data(*, file: str, data) -> None:
    try:
        with open(file, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False)
    except (yaml.YAMLError, IOError) as e:
        log_message(f"Error writing YAML: {e}")


def get_schema_version() -> str:
    data = get_yaml_data(file=SCHEMA_VERSION_ENV_FILE)
    schema_version = data.get(SCHEMA_VERSION_ENV_NAME, DEFAULT_SCHEMA_VERSION)
    return schema_version


def set_schema_version(*, version: str) -> None:
    if version is not None and version != "":
        set_yaml_data(
            file=SCHEMA_VERSION_ENV_FILE, data={SCHEMA_VERSION_ENV_NAME: version}
        )
    return
