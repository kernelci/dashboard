from typing import Union, TypedDict, Optional
from kernelCI_app.helpers.filters import UNKNOWN_STRING
from kernelCI_app.utils import sanitize_dict


class Misc(TypedDict, total=False):
    platform: str
    lab: Optional[str]


def handle_misc(misc: Union[str, dict, None]) -> Optional[dict]:
    """
    Handle misc data (environment or build) by parsing JSON string or dict.
    Preserves all fields and sets default values for known fields.
    """

    misc = sanitize_dict(misc)
    if misc is None:
        return None

    parsed_misc = dict(misc)
    parsed_misc.setdefault("platform", UNKNOWN_STRING)

    return parsed_misc


def misc_value_or_default(misc: Optional[Misc]) -> Misc:
    """Return misc data or default if None."""
    default_misc: Misc = {
        "platform": UNKNOWN_STRING,
    }

    if misc is not None:
        return misc
    return default_misc


def get_environment_misc_value(
    *,
    full_environment_misc: bool,
    parsed_environment_misc: Optional[dict],
) -> dict:
    """Return the appropriate environment_misc value based on the full_environment_misc flag."""
    platform = parsed_environment_misc.get("platform")
    if full_environment_misc:
        return parsed_environment_misc or {"platform": platform}
    return {"platform": platform}
