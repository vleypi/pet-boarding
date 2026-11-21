from datetime import date, timedelta

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from bookings.models import Booking
from rooms.models import Room
from src.constants import ROOM_SIZES
from src.exceptions import BookingError
from src.models.bookings import validate_period


def overlapping_bookings(check_in: date, check_out: date):
    """Активные бронирования, которые пересекаются с периодом"""
    return Booking.objects.filter(
        is_cancelled=False,
        check_in__lt=check_out,
        check_out__gt=check_in,
    )


def room_list(request: HttpRequest) -> HttpResponse:
    """Список мест по тарифу, при выборе размера только места этого размера"""
    size = request.GET.get("size", "")
    rooms = Room.objects.order_by("price_per_night", "name")
    if size in ROOM_SIZES:
        rooms = rooms.filter(size=size)
    else:
        size = ""
    context = {"rooms": rooms, "sizes": ROOM_SIZES, "size": size}
    return render(request, "rooms/room_list.html", context)


def available_rooms(request: HttpRequest) -> HttpResponse:
    """Поиск мест, свободных на выбранный период"""
    check_in_text = request.GET.get("check_in", "")
    check_out_text = request.GET.get("check_out", "")
    size = request.GET.get("size", "")
    if size not in ROOM_SIZES:
        size = ""
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
            busy = overlapping_bookings(check_in, check_out)
            rooms = Room.objects.exclude(
                id__in=busy.values("room_id")
            ).order_by("price_per_night", "name")
            if size:
                rooms = rooms.filter(size=size)
            context["rooms"] = rooms
    return render(request, "rooms/available.html", context)


def room_detail(request: HttpRequest, room_id: int) -> HttpResponse:
    """Карточка места: тариф, занятость сегодня и активные бронирования"""
    room = get_object_or_404(Room, pk=room_id)
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    busy_today = overlapping_bookings(today, tomorrow).filter(room=room)
    bookings = (
        room.bookings.filter(is_cancelled=False)
        .select_related("pet")
        .order_by("check_in")
    )
    context = {
        "room": room,
        "is_free": not busy_today.exists(),
        "bookings": bookings,
    }
    return render(request, "rooms/room_detail.html", context)
