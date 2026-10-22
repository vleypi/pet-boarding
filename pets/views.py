from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import fetch_all
from src.models.bookings import bookings_for_pet
from src.models.pets import find_pet_by_id
from src.models.rooms import filter_rooms_for_pet
from src.storage import load_all


def pet_list(request: HttpRequest) -> HttpResponse:
    """Список питомцев из SQLite, по выбору только те, кого можно принять"""
    only_accepted = request.GET.get("accepted") == "1"
    query = "acceptable_pets" if only_accepted else "pet_list"
    context = {"pets": fetch_all(query), "only_accepted": only_accepted}
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
