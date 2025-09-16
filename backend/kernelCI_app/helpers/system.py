from typing import Literal
from django.conf import settings

from kernelCI_app.constants.general import PRODUCTION_HOST

type PossibleHosts = Literal["production", "staging"]


def get_running_instance() -> PossibleHosts | None:
    if (
        hasattr(settings, "CORS_ALLOWED_ORIGINS")
        and PRODUCTION_HOST in settings.CORS_ALLOWED_ORIGINS
    ):
        return "production"
    elif hasattr(settings, "DEBUG") and settings.DEBUG is False:
        return "staging"
    return
