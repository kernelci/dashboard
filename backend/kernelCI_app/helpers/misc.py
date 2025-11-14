from typing import Union, TypedDict, Optional
from kernelCI_app.helpers.filters import UNKNOWN_STRING
from kernelCI_app.utils import sanitize_dict


class Misc(TypedDict):
    platform: str
    lab: Optional[str]


def handle_misc(misc: Union[str, dict, None]) -> Optional[Misc]:
    """
    Handle misc data (environment or build) by parsing JSON string or dict.
    Also sets some default values and returns only the necessary fields.
    """

    misc = sanitize_dict(misc)
    if misc is None:
        return None

    parsed_misc: Misc = {}
    parsed_misc["platform"] = misc.get("platform", UNKNOWN_STRING)
    if "lab" in misc:
        parsed_misc["lab"] = misc.get("lab")

    return parsed_misc


def misc_value_or_default(misc: Optional[Misc]) -> Misc:
    """Return misc data or default if None."""
    default_misc: Misc = {
        "platform": UNKNOWN_STRING,
    }

    if misc is not None:
        return misc
    return default_misc
