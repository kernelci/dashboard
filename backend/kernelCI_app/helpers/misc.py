from typing import Union, TypedDict, Optional
from kernelCI_app.helpers.filters import UNKNOWN_STRING
from kernelCI_app.utils import string_to_json


class EnvironmentMisc(TypedDict):
    platform: str


class BuildMisc(TypedDict):
    platform: str


def handle_environment_misc(misc: Union[str, dict, None]) -> Optional[EnvironmentMisc]:
    parsed_misc: EnvironmentMisc = {}

    if isinstance(misc, str):
        misc = string_to_json(misc)
        if misc is None:
            return None
    elif not isinstance(misc, dict):
        return None

    parsed_misc["platform"] = misc.get("platform", UNKNOWN_STRING)

    return parsed_misc


def handle_build_misc(misc: Union[str, dict, None]) -> Optional[BuildMisc]:
    parsed_misc: BuildMisc = {}

    if isinstance(misc, str):
        misc = string_to_json(misc)
        if misc is None:
            return None
    elif not isinstance(misc, dict):
        return None

    parsed_misc["platform"] = misc.get("platform", UNKNOWN_STRING)

    return parsed_misc


def env_misc_value_or_default(misc: Optional[EnvironmentMisc]) -> EnvironmentMisc:
    default_misc: EnvironmentMisc = {
        "platform": UNKNOWN_STRING,
    }

    if misc is not None:
        return misc
    return default_misc


def build_misc_value_or_default(misc: Optional[BuildMisc]) -> BuildMisc:
    default_misc: BuildMisc = {
        "platform": UNKNOWN_STRING,
    }

    if misc is not None:
        return misc
    return default_misc
