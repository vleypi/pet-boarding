from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.models.bookings import bookings_for_pet
from src.models.pets import find_pet_by_id, sort_pets_by_weight
from src.models.rooms import filter_rooms_for_pet
from src.storage import load_all, load_pets, load_users


def pet_list(request: HttpRequest) -> HttpResponse:
    """Список питомцев, упорядоченный по весу"""
    context = {"pets": sort_pets_by_weight(load_pets(load_users()))}
    return render(request, "pets/pet_list.html", context)


def pet_detail(request: HttpRequest, pet_id: int) -> HttpResponse:
    """Карточка питомца: владелец, допуск, подходящие места и история"""
    _, rooms, pets, bookings = load_all()
    pet = find_pet_by_id(pets, pet_id)
    context = {"pet": pet}
    if pet is not None:
        context["reason"] = pet.rejection_reason()
        context["room_size"] = pet.required_room_size()
        context["rooms"] = filter_rooms_for_pet(rooms, pet)
        context["bookings"] = bookings_for_pet(bookings, pet)
    return render(
        request,
        "pets/pet_detail.html",
        context,
        status=404 if pet is None else 200,
    )
