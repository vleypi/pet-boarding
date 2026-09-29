from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from homepage.views import (
    back_link,
    empty_row,
    format_period,
    not_found,
    object_link,
    page,
    status_badge,
)
from src.models import Booking
from src.models.bookings import find_booking_by_id, sort_bookings_by_date
from src.storage import load_all


def booking_row(booking: Booking) -> str:
    """Собрать строку таблицы бронирований"""
    number = object_link("booking_detail", booking.id, f"№ {booking.id}")
    pet = object_link("pet_detail", booking.pet.id, booking.pet.name)
    room = object_link("room_detail", booking.room.id, booking.room.name)
    return (
        f"<tr><td>{number}</td><td>{pet}</td><td>{room}</td>"
        f"<td>{format_period(booking)}</td>"
        f"<td>{status_badge(booking)}</td></tr>"
    )


def booking_list(request: HttpRequest) -> HttpResponse:
    """Список бронирований, упорядоченный по дате заезда"""
    _, _, _, bookings = load_all()
    rows = "".join(
        booking_row(booking) for booking in sort_bookings_by_date(bookings)
    ) or empty_row(5, "Бронирований нет")
    content = f"""
<h1 class="h2 mb-3">Бронирования</h1>
<div class="table-responsive">
<table class="table table-hover bg-white align-middle">
<thead><tr><th>Номер</th><th>Питомец</th><th>Место</th>
<th>Период</th><th>Статус</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>
"""
    return HttpResponse(page("Бронирования", content))


def booking_detail(request: HttpRequest, booking_id: int) -> HttpResponse:
    """Карточка бронирования: питомец, владелец, место, срок и стоимость"""
    _, _, _, bookings = load_all()
    booking = find_booking_by_id(bookings, booking_id)
    if booking is None:
        return not_found(
            "Бронирование не найдено",
            "booking_list",
            "К списку бронирований",
        )

    title = f"Бронирование № {booking.id}"
    pet = object_link("pet_detail", booking.pet.id, booking.pet.name)
    room = object_link("room_detail", booking.room.id, booking.room.name)
    owner = booking.pet.owner
    contacts = f"{escape(owner.name)}, {escape(owner.phone)}"
    content = f"""
<div class="card mb-4"><div class="card-body">
<h1 class="h3 card-title">{title}</h1>
<p class="card-text mb-1">Питомец: {pet}</p>
<p class="card-text mb-1">Владелец: {contacts}</p>
<p class="card-text mb-1">Место: {room}, {booking.room.size}</p>
<p class="card-text mb-1">Период: {format_period(booking)}</p>
<p class="card-text mb-1">Срок: {booking.nights} суток</p>
<p class="card-text mb-3">Стоимость: {booking.cost} ₽</p>
{status_badge(booking)}
</div></div>
{back_link("booking_list", "К списку бронирований")}
"""
    return HttpResponse(page(title, content))
