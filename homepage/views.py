from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from bookings.models import Booking
from src.constants import (
    ALLOWED_SPECIES,
    MEDIUM_ROOM_MAX_WEIGHT,
    MIN_AGE_MONTHS,
    SIZE_LARGE,
    SIZE_MEDIUM,
    SIZE_SMALL,
    SMALL_ROOM_MAX_WEIGHT,
)

UPCOMING_LIMIT = 3


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: описание гостиницы, условия приёма и разделы"""
    active = Booking.objects.active()
    context = {
        "species": sorted(ALLOWED_SPECIES),
        "min_age_months": MIN_AGE_MONTHS,
        "size_small": SIZE_SMALL,
        "size_medium": SIZE_MEDIUM,
        "size_large": SIZE_LARGE,
        "small_max": SMALL_ROOM_MAX_WEIGHT,
        "medium_max": MEDIUM_ROOM_MAX_WEIGHT,
        "active_count": active.count(),
        "upcoming": active.filter(check_in__gte=timezone.localdate())
        .order_by("check_in")
        .values(
            "id",
            "check_in",
            pet_name=F("pet__name"),
            room_name=F("room__name"),
        )[:UPCOMING_LIMIT],
    }
    return render(request, "homepage/index.html", context)
