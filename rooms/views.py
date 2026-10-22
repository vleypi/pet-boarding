from datetime import timedelta

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from src.models.bookings import active_bookings_for_room, is_room_available
from src.models.rooms import find_room_by_id, sort_rooms_by_price
from src.storage import load_all, load_rooms


def room_list(request: HttpRequest) -> HttpResponse:
    """Список мест, упорядоченный по тарифу"""
    context = {"rooms": sort_rooms_by_price(load_rooms())}
    return render(request, "rooms/room_list.html", context)


def room_detail(request: HttpRequest, room_id: int) -> HttpResponse:
    """Карточка места: тариф, занятость сегодня и активные бронирования"""
    _, rooms, _, bookings = load_all()
    room = find_room_by_id(rooms, room_id)
    context = {"room": room}
    if room is not None:
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        context["is_free"] = is_room_available(
            bookings, room, today, tomorrow
        )
        context["bookings"] = active_bookings_for_room(bookings, room)
    return render(
        request,
        "rooms/room_detail.html",
        context,
        status=404 if room is None else 200,
    )
