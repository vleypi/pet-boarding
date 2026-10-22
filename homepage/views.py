from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from db.database import fetch_all, fetch_one

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
    context = {
        "species": sorted(ALLOWED_SPECIES),
        "min_age_months": MIN_AGE_MONTHS,
        "size_small": SIZE_SMALL,
        "size_medium": SIZE_MEDIUM,
        "size_large": SIZE_LARGE,
        "small_max": SMALL_ROOM_MAX_WEIGHT,
        "medium_max": MEDIUM_ROOM_MAX_WEIGHT,
        "active_count": fetch_one("active_bookings_count")["bookings_count"],
        "upcoming": fetch_all(
            "upcoming_check_ins",
            (timezone.localdate().isoformat(), UPCOMING_LIMIT),
        ),
    }
    return render(request, "homepage/index.html", context)
