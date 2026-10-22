from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import fetch_all, fetch_one
from src.models.bookings import find_booking_by_id
from src.storage import load_all

DEFAULT_POPULAR_THRESHOLD = 2


def booking_list(request: HttpRequest) -> HttpResponse:
    """Список бронирований из SQLite, по выбору только активные"""
    only_active = request.GET.get("active") == "1"
    query = "active_booking_list" if only_active else "booking_list"
    context = {"bookings": fetch_all(query), "only_active": only_active}
    return render(request, "bookings/booking_list.html", context)


def popular_threshold(request: HttpRequest) -> int:
    """Прочитать из запроса порог популярности места"""
    try:
        return max(1, int(request.GET.get("min", "")))
    except ValueError:
        return DEFAULT_POPULAR_THRESHOLD


def statistics(request: HttpRequest) -> HttpResponse:
    """Статистика гостиницы по агрегатным запросам к SQLite"""
    threshold = popular_threshold(request)
    context = {
        "summary": fetch_one("income_summary"),
        "per_room": fetch_all("bookings_per_room"),
        "per_size": fetch_all("income_by_size"),
        "per_species": fetch_all("pets_by_species"),
        "owners": fetch_all("owners_with_several_pets"),
        "popular": fetch_all("popular_rooms", (threshold,)),
        "threshold": threshold,
    }
    return render(request, "bookings/statistics.html", context)


def booking_detail(request: HttpRequest, booking_id: int) -> HttpResponse:
    """Карточка бронирования: питомец, владелец, место, срок и стоимость"""
    _, _, _, bookings = load_all()
    booking = find_booking_by_id(bookings, booking_id)
    return render(
        request,
        "bookings/booking_detail.html",
        {"booking": booking},
        status=404 if booking is None else 200,
    )
