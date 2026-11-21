from django.contrib import messages
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
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from bookings.forms import SORT_FIELDS, BookingFilterForm, BookingForm
from bookings.models import Booking
from db.search import text_search
from pets.models import Pet
from rooms.models import Room
from src.constants import ROOM_SIZES
from users.models import User

PAGE_SIZE = 5
DEFAULT_POPULAR_THRESHOLD = 2


def stay_length(prefix: str = "") -> ExpressionWrapper:
    """Выражение ORM для срока проживания: дата выезда минус дата заезда"""
    return ExpressionWrapper(
        F(f"{prefix}check_out") - F(f"{prefix}check_in"),
        output_field=DurationField(),
    )


def filter_bookings(filters: dict):
    """Применить фильтры, поиск и сортировку к бронированиям"""
    bookings = Booking.objects.with_related()
    if filters["status"]:
        bookings = bookings.filter(status=filters["status"])
    if filters["size"]:
        bookings = bookings.filter(room__size=filters["size"])
    if filters["room"]:
        bookings = bookings.filter(room=filters["room"])
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
    """Список бронирований с формой фильтров, сортировкой и страницами"""
    form = BookingFilterForm(request.GET)
    bookings = filter_bookings(form.filters())
    page_obj = Paginator(bookings, PAGE_SIZE).get_page(
        request.GET.get("page")
    )
    context = {"page_obj": page_obj, "form": form}
    return render(request, "bookings/booking_list.html", context)


def booking_detail(request: HttpRequest, booking_id: int) -> HttpResponse:
    """Карточка бронирования: питомец, владелец, место, срок и стоимость"""
    booking = get_object_or_404(
        Booking.objects.with_related(),
        pk=booking_id,
    )
    return render(
        request,
        "bookings/booking_detail.html",
        {"booking": booking},
    )


def initial_from_query(request: HttpRequest) -> dict:
    """Начальные питомец и место из ссылок «Забронировать»"""
    initial = {}
    pet_id = request.GET.get("pet", "")
    if pet_id.isdigit():
        initial["pet"] = Pet.objects.filter(pk=int(pet_id)).first()
    room_slug = request.GET.get("room", "")
    if room_slug:
        initial["room"] = Room.objects.filter(slug=room_slug).first()
    return {key: value for key, value in initial.items() if value}


def booking_create(request: HttpRequest) -> HttpResponse:
    """Форма новой брони: GET показывает форму, POST проверяет и сохраняет"""
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(
                request, f"Бронирование № {booking.pk} оформлено"
            )
            return redirect(booking)
    else:
        form = BookingForm(initial=initial_from_query(request))
    context = {"form": form, "title": "Новое бронирование"}
    return render(request, "bookings/booking_form.html", context)


def booking_update(request: HttpRequest, booking_id: int) -> HttpResponse:
    """Изменение активной брони той же формой с instance"""
    booking = get_object_or_404(Booking.objects.active(), pk=booking_id)
    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request,
                             f"Бронирование № {booking.pk} изменено")
            return redirect(booking)
    else:
        form = BookingForm(instance=booking)
    context = {
        "form": form,
        "booking": booking,
        "title": f"Изменение бронирования № {booking.pk}",
    }
    return render(request, "bookings/booking_form.html", context)


@require_POST
def booking_cancel(request: HttpRequest, booking_id: int) -> HttpResponse:
    """Отменить активную бронь: запись остаётся, меняется статус"""
    booking = get_object_or_404(Booking.objects.active(), pk=booking_id)
    booking.cancel()
    messages.success(request, f"Бронирование № {booking.pk} отменено, "
                              "место освободилось")
    return redirect(booking)


def popular_threshold(request: HttpRequest) -> int:
    """Прочитать из запроса порог популярности места"""
    try:
        return max(1, int(request.GET.get("min", "")))
    except ValueError:
        return DEFAULT_POPULAR_THRESHOLD


def rooms_with_stats():
    """Места с числом оплачиваемых броней, сутками и выручкой по каждому"""
    active = ~Q(bookings__status=Booking.Status.CANCELLED)
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
    summary = Booking.objects.billable().aggregate(
        stay=Sum(stay_length()),
        average_stay=Avg(stay_length()),
        first_check_in=Min("check_in"),
        last_check_out=Max("check_out"),
    )
    summary.update(Booking.objects.aggregate(
        total_count=Count("id"),
        active_count=Count("id", filter=Q(status=Booking.Status.ACTIVE)),
        cancelled_count=Count(
            "id", filter=Q(status=Booking.Status.CANCELLED)
        ),
        completed_count=Count(
            "id", filter=Q(status=Booking.Status.COMPLETED)
        ),
    ))
    summary["nights"] = summary["stay"].days if summary["stay"] else 0
    summary["average_nights"] = (
        summary["average_stay"].total_seconds() / 86400
        if summary["average_stay"] else 0
    )
    summary["income"] = sum(room.income for room in rooms)
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
                "bookings",
                filter=~Q(bookings__status=Booking.Status.CANCELLED),
            )
        )
        .filter(bookings_count__gte=threshold)
        .order_by("-bookings_count", "name"),
        "threshold": threshold,
    }
    return render(request, "bookings/statistics.html", context)
