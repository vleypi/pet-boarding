from datetime import date
from typing import Optional

from django.core.paginator import Paginator
from django.db.models import (
    Avg,
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    Max,
    Min,
    Q,
    Sum,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from bookings.models import Booking
from db.search import text_search
from pets.models import Pet
from rooms.models import Room
from src.constants import ROOM_SIZES
from users.models import User

PAGE_SIZE = 5
DEFAULT_POPULAR_THRESHOLD = 2

STATUS_FILTERS = {
    "active": Q(is_cancelled=False),
    "cancelled": Q(is_cancelled=True),
}

SORT_FIELDS = {
    "check_in": ("check_in", "pk"),
    "-check_in": ("-check_in", "-pk"),
    "pet": ("pet__name", "check_in"),
    "owner": ("pet__owner__name", "pet__name", "check_in"),
    "room": ("room__name", "check_in"),
    "price": ("-room__price_per_night", "check_in"),
}
SORT_TITLES = {
    "check_in": "сначала ранние заезды",
    "-check_in": "сначала поздние заезды",
    "pet": "по кличке питомца",
    "owner": "по владельцу",
    "room": "по месту",
    "price": "сначала дорогие места",
}
DEFAULT_SORT = "check_in"


def stay_length(prefix: str = "") -> ExpressionWrapper:
    """Выражение ORM для срока проживания: дата выезда минус дата заезда"""
    return ExpressionWrapper(
        F(f"{prefix}check_out") - F(f"{prefix}check_in"),
        output_field=DurationField(),
    )


def parse_date(text: str, title: str, errors: list[str]) -> Optional[date]:
    """Разобрать дату из параметра запроса, при ошибке добавить сообщение"""
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        errors.append(f"{title}: нужна дата в формате ГГГГ-ММ-ДД")
        return None


def read_filters(request: HttpRequest) -> dict:
    """Прочитать и проверить параметры фильтрации списка бронирований"""
    errors: list[str] = []
    status = request.GET.get("status", "")
    if status not in STATUS_FILTERS:
        status = ""
    size = request.GET.get("size", "")
    if size not in ROOM_SIZES:
        size = ""
    room = request.GET.get("room", "")
    if not room.isdigit():
        room = ""
    sort = request.GET.get("sort", DEFAULT_SORT)
    if sort not in SORT_FIELDS:
        sort = DEFAULT_SORT
    date_from = parse_date(request.GET.get("date_from", ""), "Заезд с",
                           errors)
    date_to = parse_date(request.GET.get("date_to", ""), "Заезд по", errors)
    if date_from and date_to and date_from > date_to:
        errors.append("начало периода позже его окончания")
        date_from = date_to = None
    return {
        "q": request.GET.get("q", "").strip(),
        "status": status,
        "size": size,
        "room": room,
        "date_from": date_from,
        "date_to": date_to,
        "sort": sort,
        "errors": errors,
    }


def filter_bookings(filters: dict):
    """Применить фильтры, поиск и сортировку к бронированиям"""
    bookings = Booking.objects.select_related("pet__owner", "room")
    if filters["status"]:
        bookings = bookings.filter(STATUS_FILTERS[filters["status"]])
    if filters["size"]:
        bookings = bookings.filter(room__size=filters["size"])
    if filters["room"]:
        bookings = bookings.filter(room_id=int(filters["room"]))
    if filters["date_from"]:
        bookings = bookings.filter(check_in__gte=filters["date_from"])
    if filters["date_to"]:
        bookings = bookings.filter(check_in__lte=filters["date_to"])
    if filters["q"]:
        bookings = bookings.filter(
            text_search(filters["q"], "pet__name", "pet__owner__name")
        )
    return bookings.order_by(*SORT_FIELDS[filters["sort"]])


def booking_list(request: HttpRequest) -> HttpResponse:
    """Список бронирований с фильтрами, поиском, сортировкой и страницами"""
    filters = read_filters(request)
    bookings = filter_bookings(filters)
    page_obj = Paginator(bookings, PAGE_SIZE).get_page(
        request.GET.get("page")
    )
    context = {
        "page_obj": page_obj,
        "filters": filters,
        "rooms": Room.objects.only("id", "name"),
        "sizes": ROOM_SIZES,
        "statuses": {"active": "активные", "cancelled": "отменённые"},
        "sort_titles": SORT_TITLES,
    }
    return render(request, "bookings/booking_list.html", context)


def booking_detail(request: HttpRequest, booking_id: int) -> HttpResponse:
    """Карточка бронирования: питомец, владелец, место, срок и стоимость"""
    booking = get_object_or_404(
        Booking.objects.select_related("pet__owner", "room"),
        pk=booking_id,
    )
    return render(
        request,
        "bookings/booking_detail.html",
        {"booking": booking},
    )


def popular_threshold(request: HttpRequest) -> int:
    """Прочитать из запроса порог популярности места"""
    try:
        return max(1, int(request.GET.get("min", "")))
    except ValueError:
        return DEFAULT_POPULAR_THRESHOLD


def rooms_with_stats():
    """Места с числом активных броней, сутками и выручкой по каждому"""
    active = Q(bookings__is_cancelled=False)
    rooms = list(
        Room.objects.annotate(
            bookings_count=Count("bookings", filter=active),
            stay=Sum(stay_length("bookings__"), filter=active),
        ).order_by("-bookings_count", "name")
    )
    for room in rooms:
        room.nights = room.stay.days if room.stay else 0
        room.income = room.nights * room.price_per_night
    return rooms


def income_by_size(rooms: list) -> list[dict]:
    """Сгруппировать выручку и брони мест по размеру"""
    groups = {size: {"size": size, "bookings_count": 0, "income": 0}
              for size in ROOM_SIZES}
    for room in rooms:
        groups[room.size]["bookings_count"] += room.bookings_count
        groups[room.size]["income"] += room.income
    return sorted(groups.values(), key=lambda row: row["income"],
                  reverse=True)


def statistics(request: HttpRequest) -> HttpResponse:
    """Статистика гостиницы на агрегатных запросах ORM"""
    threshold = popular_threshold(request)
    rooms = rooms_with_stats()
    summary = Booking.objects.filter(is_cancelled=False).aggregate(
        bookings_count=Count("id"),
        stay=Sum(stay_length()),
        average_stay=Avg(stay_length()),
        first_check_in=Min("check_in"),
        last_check_out=Max("check_out"),
    )
    summary["nights"] = summary["stay"].days if summary["stay"] else 0
    summary["average_nights"] = (
        summary["average_stay"].total_seconds() / 86400
        if summary["average_stay"] else 0
    )
    summary["income"] = sum(room.income for room in rooms)
    summary["cancelled_count"] = Booking.objects.filter(
        is_cancelled=True
    ).count()
    context = {
        "summary": summary,
        "per_room": rooms,
        "per_size": income_by_size(rooms),
        "per_species": Pet.objects.values("species")
        .annotate(pets_count=Count("id"), average_weight=Avg("weight_kg"))
        .order_by("-pets_count", "species"),
        "owners": User.objects.annotate(pets_count=Count("pets"))
        .filter(pets_count__gt=1)
        .order_by("-pets_count", "name"),
        "popular": Room.objects.annotate(
            bookings_count=Count(
                "bookings", filter=Q(bookings__is_cancelled=False)
            )
        )
        .filter(bookings_count__gte=threshold)
        .order_by("-bookings_count", "name"),
        "threshold": threshold,
    }
    return render(request, "bookings/statistics.html", context)
