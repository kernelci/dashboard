from django.apps import AppConfig
from kernelCI_app.cache import run_cache_invalidator


class KernelciAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kernelCI_app"

    def ready(self) -> None:
        run_cache_invalidator()
        return super().ready()
