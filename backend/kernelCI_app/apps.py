from django.apps import AppConfig
from kernelCI_app.cache import runCacheInvalidator


class KernelciAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kernelCI_app"

    def ready(self) -> None:
        runCacheInvalidator()
        return super().ready()
