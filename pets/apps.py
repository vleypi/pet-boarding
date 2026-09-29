from django.apps import AppConfig


class PetsConfig(AppConfig):
    """Настройки приложения питомцев"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "pets"
