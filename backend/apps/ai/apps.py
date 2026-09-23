from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai"
    verbose_name = "AI匹配"

    def ready(self) -> None:
        from . import signals  # noqa: F401
