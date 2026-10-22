from datetime import date, timedelta

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from db.database import fetch_all
from src.constants import ROOM_SIZES
from src.exceptions import BookingError
from src.models.bookings import (
    active_bookings_for_room,
    is_room_available,
    validate_period,
)
from src.models.rooms import find_room_by_id
from src.storage import load_all


def room_list(request: HttpRequest) -> HttpResponse:
    """Список мест из SQLite, при выборе размера только места этого размера"""
    size = request.GET.get("size", "")
    if size in ROOM_SIZES:
        rooms = fetch_all("rooms_by_size", (size,))
    else:
        size = ""
        rooms = fetch_all("room_list")
    context = {"rooms": rooms, "sizes": ROOM_SIZES, "size": size}
    return render(request, "rooms/room_list.html", context)


def available_rooms(request: HttpRequest) -> HttpResponse:
    """Поиск мест, свободных на выбранный период"""
    check_in_text = request.GET.get("check_in", "")
    check_out_text = request.GET.get("check_out", "")
    size = request.GET.get("size", "")
    context = {
        "check_in": check_in_text,
        "check_out": check_out_text,
        "size": size,
        "sizes": ROOM_SIZES,
        "rooms": None,
        "error": "",
    }
    if check_in_text and check_out_text:
        try:
            check_in = date.fromisoformat(check_in_text)
            check_out = date.fromisoformat(check_out_text)
            validate_period(check_in, check_out)
        except ValueError:
            context["error"] = "даты нужно указать в формате ГГГГ-ММ-ДД"
        except BookingError as error:
            context["error"] = str(error)
        else:
            context["rooms"] = fetch_all(
                "available_rooms",
                (check_out.isoformat(), check_in.isoformat(), size, size),
            )
    return render(request, "rooms/available.html", context)


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
