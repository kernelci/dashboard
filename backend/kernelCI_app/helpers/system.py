from typing import Literal
from django.conf import settings

from kernelCI_app.constants.general import PRODUCTION_HOST


# TODO: combine with the function below once it is verified
# that this way of identifying the production instance works
def is_production_instance():
    if not hasattr(settings, "CORS_ALLOWED_ORIGINS"):
        return False
    if PRODUCTION_HOST in settings.CORS_ALLOWED_ORIGINS:
        return True
    return False


type PossibleHosts = Literal["production", "staging"]


# TODO: verify if this is the correct way to identify
# the production instance
def get_running_instance() -> PossibleHosts | None:
    if (
        hasattr(settings, "CORS_ALLOWED_ORIGINS")
        and PRODUCTION_HOST in settings.CORS_ALLOWED_ORIGINS
    ):
        return "production"
    elif hasattr(settings, "DEBUG") and settings.DEBUG is False:
        return "staging"
    return
