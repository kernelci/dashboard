from typing import Union


def isBooleanOrStringTrue(value: Union[bool, str]) -> bool:
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower() == "true"
    else:
        raise ValueError("Value must be a boolean or string")
