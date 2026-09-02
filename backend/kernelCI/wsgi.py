"""
WSGI config for kernelCI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from prometheus_client import Gauge

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kernelCI.settings")

application = get_wsgi_application()

Gauge(
    "dashboard_build_info",
    "Deployed backend version, always reported as 1",
    ["version"],
    multiprocess_mode="max",
).labels(version=os.environ.get("DASHBOARD_VERSION") or "unknown").set(1)
