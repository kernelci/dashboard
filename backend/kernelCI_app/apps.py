import os
import sys
import threading

from django.apps import AppConfig


class KernelciAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kernelCI_app"

    def ready(self) -> None:
        super().ready()
        is_server = (
            os.path.basename(sys.argv[0]) == "gunicorn" or "runserver" in sys.argv
        )
        if not is_server:
            return
        if "runserver" in sys.argv and os.environ.get("RUN_MAIN") != "true":
            return

        from django.core.cache import cache

        from kernelCI_app.queries.notifications import warm_metrics_cache

        # Single-flight via atomic Redis add: only one worker warms per deploy.
        if not cache.add("metrics_startup_warm_lock", 1, timeout=600):
            return
        threading.Thread(target=warm_metrics_cache, daemon=True).start()
