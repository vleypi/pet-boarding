from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.models.bookings import find_booking_by_id, sort_bookings_by_date
from src.storage import load_all


def booking_list(request: HttpRequest) -> HttpResponse:
    """Список бронирований, упорядоченный по дате заезда"""
    _, _, _, bookings = load_all()
    context = {"bookings": sort_bookings_by_date(bookings)}
    return render(request, "bookings/booking_list.html", context)


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
