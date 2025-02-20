from typing import Union
from django.http import HttpResponseBadRequest
from kernelCI_app.utils import getErrorResponseBody


def isBooleanOrStringTrue(value: Union[bool, str]) -> bool:
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower() == "true"
    else:
        raise ValueError("Value must be a boolean or string")


def validate_required_params(request, required_params: list[str]):
    for p in required_params:
        if not request.GET.get(p):
            return HttpResponseBadRequest(
                getErrorResponseBody(f"missing required field `{p}`")
            )
