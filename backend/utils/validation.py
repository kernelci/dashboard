from typing import Union
from django.http import HttpResponseBadRequest
from kernelCI_app.utils import get_error_body_response


def is_boolean_or_string_true(value: Union[bool, str]) -> bool:
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
                get_error_body_response(f"missing required field `{p}`")
            )
