from django.apps import AppConfig


class BookingsConfig(AppConfig):
    """Настройки приложения бронирований"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "bookings"
