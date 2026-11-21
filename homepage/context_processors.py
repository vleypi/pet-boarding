from django.http import HttpRequest

from bookings.models import Booking
from rooms.models import Room

SITE_NAME = "Передержка"


def site_info(request: HttpRequest) -> dict:
    """Общие данные для всех шаблонов: название и счётчики в навигации"""
    return {
        "site_name": SITE_NAME,
        "rooms_count": Room.objects.count(),
        "active_bookings_count": Booking.objects.active().count(),
    }
