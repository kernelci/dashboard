from django.conf import settings

from kernelCI_app.constants.general import PRODUCTION_HOST


def is_production_instance():
    if not hasattr(settings, "CORS_ALLOWED_ORIGINS"):
        return False
    if PRODUCTION_HOST in settings.CORS_ALLOWED_ORIGINS:
        return True
    return False
