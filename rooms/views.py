from datetime import timedelta

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from homepage.views import back_link, format_period, not_found, page
from src.models import Booking, Room
from src.models.bookings import active_bookings_for_room, is_room_available
from src.models.rooms import find_room_by_id, sort_rooms_by_price
from src.storage import load_all, load_rooms


def room_row(room: Room) -> str:
    """Собрать строку таблицы мест"""
    url = reverse("room_detail", args=[room.id])
    return (
        f'<tr><td><a href="{url}">{escape(room.name)}</a></td>'
        f"<td>{room.size}</td>"
        f'<td class="text-end">{room.price_per_night}</td></tr>'
    )


def room_booking_item(booking: Booking) -> str:
    """Собрать пункт списка бронирований места"""
    url = reverse("booking_detail", args=[booking.id])
    return (
        f'<li class="list-group-item"><a href="{url}">'
        f"{escape(booking.pet.name)}</a>: {format_period(booking)}</li>"
    )


def room_list(request: HttpRequest) -> HttpResponse:
    """Список мест, упорядоченный по тарифу"""
    rooms = sort_rooms_by_price(load_rooms())
    rows = "".join(room_row(room) for room in rooms)
    if not rows:
        rows = '<tr><td colspan="3" class="text-muted">Мест нет</td></tr>'
    content = f"""
<h1 class="h2 mb-3">Места</h1>
<div class="table-responsive">
<table class="table table-hover bg-white">
<thead><tr><th>Название</th><th>Размер</th>
<th class="text-end">Тариф в сутки, ₽</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>
"""
    return HttpResponse(page("Места", content))


def room_detail(request: HttpRequest, room_id: int) -> HttpResponse:
    """Карточка места: тариф, занятость сегодня и активные бронирования"""
    _, rooms, _, bookings = load_all()
    room = find_room_by_id(rooms, room_id)
    if room is None:
        return not_found("Место не найдено", "room_list", "К списку мест")

    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    is_free = is_room_available(bookings, room, today, tomorrow)
    status = "свободно сегодня" if is_free else "занято сегодня"
    badge = "text-bg-success" if is_free else "text-bg-danger"

    items = "".join(
        room_booking_item(booking)
        for booking in active_bookings_for_room(bookings, room)
    )
    if not items:
        items = '<li class="list-group-item text-muted">Бронирований нет</li>'

    content = f"""
<div class="card mb-4"><div class="card-body">
<h1 class="h3 card-title">{escape(room.name)}</h1>
<p class="card-text mb-1">Размер: {room.size}</p>
<p class="card-text mb-3">Тариф: {room.price_per_night} ₽ в сутки</p>
<span class="badge {badge}">{status}</span>
</div></div>
<h2 class="h5">Активные бронирования</h2>
<ul class="list-group mb-4">{items}</ul>
{back_link("room_list", "К списку мест")}
"""
    return HttpResponse(page(room.name, content))
