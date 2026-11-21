from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from db.search import text_search
from pets.models import Pet
from rooms.models import Room
from src.constants import ALLOWED_SPECIES, MIN_AGE_MONTHS


def pet_list(request: HttpRequest) -> HttpResponse:
    """Список питомцев с поиском и фильтром «можно принять»"""
    only_accepted = request.GET.get("accepted") == "1"
    query = request.GET.get("q", "").strip()
    pets = Pet.objects.annotate(owner_name=F("owner__name")).order_by(
        "weight_kg", "name"
    )
    if only_accepted:
        pets = pets.filter(
            species__in=ALLOWED_SPECIES,
            age_months__gte=MIN_AGE_MONTHS,
            is_vaccinated=True,
        )
    if query:
        pets = pets.filter(text_search(query, "name", "owner__name"))
    context = {"pets": pets, "only_accepted": only_accepted, "query": query}
    return render(request, "pets/pet_list.html", context)


def pet_detail(request: HttpRequest, pet_id: int) -> HttpResponse:
    """Карточка питомца: владелец, допуск, подходящие места и история"""
    pet = get_object_or_404(Pet.objects.select_related("owner"), pk=pet_id)
    room_size = pet.required_room_size()
    context = {
        "pet": pet,
        "reason": pet.rejection_reason(),
        "room_size": room_size,
        "rooms": Room.objects.filter(size=room_size).order_by(
            "price_per_night", "name"
        ),
        "bookings": pet.bookings.select_related("room").order_by("check_in"),
    }
    return render(request, "pets/pet_detail.html", context)
