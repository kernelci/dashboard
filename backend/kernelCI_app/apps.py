from django.apps import AppConfig


class KernelciAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kernelCI_app"

    def ready(self) -> None:
        return super().ready()
