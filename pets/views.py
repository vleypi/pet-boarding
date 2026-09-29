from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import escape

from homepage.views import (
    back_link,
    format_period,
    not_found,
    page,
    status_badge,
)
from src.models import Booking, Pet, Room
from src.models.bookings import bookings_for_pet
from src.models.pets import find_pet_by_id, sort_pets_by_weight
from src.models.rooms import filter_rooms_for_pet
from src.storage import load_all, load_pets, load_users


def pet_row(pet: Pet) -> str:
    """Собрать строку таблицы питомцев"""
    url = reverse("pet_detail", args=[pet.id])
    return (
        f'<tr><td><a href="{url}">{escape(pet.name)}</a></td>'
        f"<td>{escape(pet.species)}</td>"
        f'<td class="text-end">{pet.weight_kg}</td>'
        f"<td>{escape(pet.owner.name)}</td></tr>"
    )


def acceptance_badge(pet: Pet) -> str:
    """Собрать бейдж допуска питомца с причиной отказа"""
    reason = pet.rejection_reason()
    if not reason:
        return '<span class="badge text-bg-success">можно принять</span>'
    return (
        '<span class="badge text-bg-danger">нельзя принять</span> '
        f'<span class="text-muted">{escape(reason)}</span>'
    )


def room_item(room: Room) -> str:
    """Собрать пункт списка подходящих мест"""
    url = reverse("room_detail", args=[room.id])
    return (
        f'<li class="list-group-item"><a href="{url}">'
        f"{escape(room.name)}</a>, {room.price_per_night} ₽ в сутки</li>"
    )


def pet_booking_item(booking: Booking) -> str:
    """Собрать пункт истории бронирований питомца"""
    url = reverse("booking_detail", args=[booking.id])
    return (
        '<li class="list-group-item d-flex justify-content-between">'
        f'<span><a href="{url}">{escape(booking.room.name)}</a>, '
        f"{format_period(booking)}</span>{status_badge(booking)}</li>"
    )


def empty_item(text: str) -> str:
    """Собрать пункт списка для пустого набора данных"""
    return f'<li class="list-group-item text-muted">{text}</li>'


def pet_list(request: HttpRequest) -> HttpResponse:
    """Список питомцев, упорядоченный по весу"""
    pets = sort_pets_by_weight(load_pets(load_users()))
    rows = "".join(pet_row(pet) for pet in pets)
    if not rows:
        rows = '<tr><td colspan="4" class="text-muted">Питомцев нет</td></tr>'
    content = f"""
<h1 class="h2 mb-3">Питомцы</h1>
<div class="table-responsive">
<table class="table table-hover bg-white">
<thead><tr><th>Кличка</th><th>Вид</th>
<th class="text-end">Вес, кг</th><th>Владелец</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>
"""
    return HttpResponse(page("Питомцы", content))


def pet_detail(request: HttpRequest, pet_id: int) -> HttpResponse:
    """Карточка питомца: владелец, допуск, подходящие места и история"""
    _, rooms, pets, bookings = load_all()
    pet = find_pet_by_id(pets, pet_id)
    if pet is None:
        return not_found("Питомец не найден", "pet_list", "К списку питомцев")

    vaccinated = "есть" if pet.is_vaccinated else "нет"
    rooms_items = "".join(
        room_item(room) for room in filter_rooms_for_pet(rooms, pet)
    ) or empty_item("Подходящих мест нет")
    history = "".join(
        pet_booking_item(booking)
        for booking in bookings_for_pet(bookings, pet)
    ) or empty_item("Бронирований нет")

    content = f"""
<div class="card mb-4"><div class="card-body">
<h1 class="h3 card-title">{escape(pet.name)}</h1>
<p class="card-text mb-1">Вид: {escape(pet.species)}</p>
<p class="card-text mb-1">Возраст: {pet.age_months} месяцев</p>
<p class="card-text mb-1">Вес: {pet.weight_kg} кг</p>
<p class="card-text mb-1">Прививки: {vaccinated}</p>
<p class="card-text mb-3">Владелец: {escape(pet.owner.name)},
{escape(pet.owner.phone)}</p>
{acceptance_badge(pet)}
</div></div>
<h2 class="h5">Подходящие места: {pet.required_room_size()}</h2>
<ul class="list-group mb-4">{rooms_items}</ul>
<h2 class="h5">История бронирований</h2>
<ul class="list-group mb-4">{history}</ul>
{back_link("pet_list", "К списку питомцев")}
"""
    return HttpResponse(page(pet.name, content))
