from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.utils import timezone

from bookings.models import Booking
from db.search import text_search
from pets.models import Pet
from rooms.models import Room
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def hotel():
    """Небольшая гостиница: два владельца, три питомца, три места, брони"""
    anna = User.objects.create(name="Иванова Анна", phone="+7 1")
    sergey = User.objects.create(name="Петров Сергей", phone="+7 2")
    barsik = Pet.objects.create(name="Барсик", species="кошка",
                                age_months=18, weight_kg=4.5,
                                is_vaccinated=True, owner=anna)
    rex = Pet.objects.create(name="Рекс", species="собака", age_months=36,
                             weight_kg=24.0, is_vaccinated=True,
                             owner=sergey)
    puppy = Pet.objects.create(name="Пушок", species="собака",
                               age_months=2, weight_kg=3.0,
                               is_vaccinated=False, owner=sergey)
    small = Room.objects.create(name="Вольер 1", size="малое",
                                price_per_night=800)
    large = Room.objects.create(name="Апартаменты 1", size="большое",
                                price_per_night=1800)
    medium = Room.objects.create(name="Комната 1", size="среднее",
                                 price_per_night=1200)
    Booking.objects.create(pet=barsik, room=small,
                           check_in=date(2026, 10, 1),
                           check_out=date(2026, 10, 8))
    Booking.objects.create(pet=rex, room=large,
                           check_in=date(2026, 10, 3),
                           check_out=date(2026, 10, 10))
    cancelled = Booking.objects.create(pet=rex, room=small,
                                       check_in=date(2026, 11, 1),
                                       check_out=date(2026, 11, 3),
                                       status=Booking.Status.CANCELLED)
    return {"anna": anna, "sergey": sergey, "barsik": barsik, "rex": rex,
            "puppy": puppy, "small": small, "large": large,
            "medium": medium, "cancelled": cancelled}


def test_relations_work_both_ways(hotel):
    """Связи доступны от брони к питомцу и обратно через related_name"""
    booking = Booking.objects.select_related("pet__owner", "room").first()
    assert booking.pet.owner.name == "Иванова Анна"
    assert list(hotel["anna"].pets.all()) == [hotel["barsik"]]
    assert hotel["small"].bookings.count() == 2
    assert hotel["rex"].bookings.active().count() == 1


def test_protect_forbids_deleting_room_with_bookings(hotel):
    """PROTECT не даёт удалить место, на которое есть брони"""
    with pytest.raises(ProtectedError):
        hotel["small"].delete()
    hotel["medium"].delete()
    assert not Room.objects.filter(name="Комната 1").exists()


def test_check_constraint_rejects_wrong_period(hotel):
    """База не принимает бронь, где выезд не позже заезда"""
    with pytest.raises(IntegrityError), transaction.atomic():
        Booking.objects.create(pet=hotel["barsik"], room=hotel["small"],
                               check_in=date(2026, 12, 5),
                               check_out=date(2026, 12, 5))


def test_cancel_saves_flag(hotel):
    """cancel и complete сохраняют статус в базе"""
    booking = Booking.objects.active().first()
    booking.cancel()
    booking.refresh_from_db()
    assert booking.status == Booking.Status.CANCELLED
    assert booking.get_status_display() == "Отменено"
    booking.complete()
    booking.refresh_from_db()
    assert booking.status == "completed"


def test_update_and_cost(hotel):
    """Изменение тарифа сохраняется и меняет стоимость брони"""
    Room.objects.filter(pk=hotel["small"].pk).update(price_per_night=1000)
    booking = Booking.objects.select_related("room").get(
        pet=hotel["barsik"]
    )
    assert booking.nights == 7
    assert booking.cost == 7000


def test_pet_rules(hotel):
    """Правила допуска и подбор места перенесены в модель"""
    assert hotel["barsik"].can_be_accepted()
    assert hotel["puppy"].rejection_reason() == "возраст меньше 3 месяцев"
    assert hotel["rex"].required_room_size() == "большое"
    assert hotel["large"].is_suitable_for(hotel["rex"])


def test_text_search_ignores_case_for_cyrillic(hotel):
    """Поиск находит кириллицу в любом регистре и по связанному полю"""
    for query in ("барсик", "БАРСИК", "арс"):
        found = Pet.objects.filter(text_search(query, "name"))
        assert list(found) == [hotel["barsik"]]
    by_owner = Pet.objects.filter(text_search("петров", "owner__name"))
    assert set(by_owner) == {hotel["rex"], hotel["puppy"]}


def test_room_list_filters_by_size(client, hotel):
    """Список мест фильтруется по размеру, неизвестный размер игнорируется"""
    response = client.get("/rooms/", {"size": "малое"})
    assert [room.name for room in response.context["rooms"]] == ["Вольер 1"]
    response = client.get("/rooms/", {"size": "огромное"})
    assert len(response.context["rooms"]) == 3


def test_available_rooms_ignore_cancelled(client, hotel):
    """Свободные места: занятые исключены, отменённая бронь не мешает"""
    response = client.get("/rooms/available/", {
        "check_in": "2026-10-05", "check_out": "2026-10-06",
    })
    names = {room.name for room in response.context["rooms"]}
    assert names == {"Комната 1"}
    response = client.get("/rooms/available/", {
        "check_in": "2026-11-01", "check_out": "2026-11-02",
    })
    assert len(response.context["rooms"]) == 3


def test_available_rooms_bad_dates(client, hotel):
    """Ошибка ввода дат показывается сообщением, а не падением"""
    response = client.get("/rooms/available/", {
        "check_in": "abc", "check_out": "2026-10-06",
    })
    assert response.status_code == 200
    assert response.context["error"]


@pytest.mark.parametrize("url", ["/rooms/net-takogo-99/", "/rooms/999/",
                                 "/pets/999/", "/bookings/999/"])
def test_missing_objects_return_404(client, hotel, url):
    """Несуществующий объект возвращает 404"""
    assert client.get(url).status_code == 404


def test_pet_list_filter_and_search(client, hotel):
    """Фильтр «можно принять» и поиск по владельцу работают вместе"""
    response = client.get("/pets/", {"accepted": "1", "q": "петров"})
    pets = list(response.context["pets"])
    assert [pet.name for pet in pets] == ["Рекс"]
    assert pets[0].owner_name == "Петров Сергей"


def test_booking_list_filters(client, hotel):
    """Фильтры по статусу, размеру места и поиску по кличке"""
    response = client.get("/bookings/", {"status": "cancelled"})
    assert response.context["page_obj"].paginator.count == 1
    response = client.get("/bookings/", {"size": "малое",
                                         "status": "active"})
    assert response.context["page_obj"].paginator.count == 1
    response = client.get("/bookings/", {"q": "рекс"})
    assert response.context["page_obj"].paginator.count == 2


def test_booking_list_sort_whitelist(client, hotel):
    """Сортировка только по разрешённым полям, остальное по умолчанию"""
    response = client.get("/bookings/", {"sort": "-check_in"})
    first = response.context["page_obj"][0]
    assert first.check_in == date(2026, 11, 1)
    response = client.get("/bookings/", {"sort": "pet__owner__phone"})
    assert response.context["filters"]["sort"] == "check_in"


def test_booking_list_bad_date_reported(client, hotel):
    """Неверная дата не применяется и выводится сообщение"""
    response = client.get("/bookings/", {"date_from": "2026-13-40"})
    assert response.context["filters"]["errors"]
    assert response.context["page_obj"].paginator.count == 3


def test_booking_pagination_keeps_params(client, hotel):
    """Страницы делятся по пять, ссылки сохраняют фильтры"""
    for day in range(1, 8):
        Booking.objects.create(pet=hotel["barsik"], room=hotel["medium"],
                               check_in=date(2027, 1, day * 2),
                               check_out=date(2027, 1, day * 2 + 1))
    response = client.get("/bookings/", {"status": "active", "page": "2"})
    page = response.context["page_obj"]
    assert page.paginator.num_pages == 2
    assert page.number == 2
    assert "status=active&amp;page=1" in response.content.decode()
    response = client.get("/bookings/", {"page": "999"})
    assert response.context["page_obj"].number == 2


def test_statistics_skips_cancelled(client, hotel):
    """Сутки и выручка не учитывают отменённые брони"""
    response = client.get("/bookings/statistics/", {"min": "2"})
    summary = response.context["summary"]
    assert summary["total_count"] == 3
    assert summary["nights"] == 14
    assert summary["income"] == 7 * 800 + 7 * 1800
    assert summary["cancelled_count"] == 1
    assert list(response.context["popular"]) == []
    per_room = {room.name: room.bookings_count
                for room in response.context["per_room"]}
    assert per_room == {"Вольер 1": 1, "Апартаменты 1": 1, "Комната 1": 0}


def test_home_shows_upcoming(client, hotel):
    """На главной ближайшие активные заезды начиная с сегодня"""
    today = timezone.localdate()
    Booking.objects.create(pet=hotel["barsik"], room=hotel["medium"],
                           check_in=today + timedelta(days=1),
                           check_out=today + timedelta(days=3))
    response = client.get("/")
    upcoming = list(response.context["upcoming"])
    assert [item["pet_name"] for item in upcoming] == ["Барсик"]
    assert response.context["active_bookings_count"] == 3
    assert response.context["rooms_count"] == 3
    assert response.context["site_name"] == "Передержка"


def test_queryset_methods(hotel):
    """Методы менеджера отбирают брони по статусу и периоду"""
    Booking.objects.filter(pet=hotel["barsik"]).update(
        status=Booking.Status.COMPLETED
    )
    assert Booking.objects.active().count() == 1
    assert Booking.objects.cancelled().count() == 1
    assert Booking.objects.completed().count() == 1
    assert Booking.objects.billable().count() == 2
    busy = Booking.objects.overlapping(date(2026, 10, 5), date(2026, 10, 6))
    assert [booking.room for booking in busy] == [hotel["large"]]


def test_completed_booking_does_not_block_room(client, hotel):
    """Завершённая бронь, как и отменённая, не занимает место"""
    Booking.objects.filter(pet=hotel["barsik"]).update(
        status=Booking.Status.COMPLETED
    )
    response = client.get("/rooms/available/", {
        "check_in": "2026-10-05", "check_out": "2026-10-06",
    })
    names = {room.name for room in response.context["rooms"]}
    assert names == {"Вольер 1", "Комната 1"}


@pytest.mark.parametrize("changes, field", [
    ({"check_in": date(2026, 10, 5), "check_out": date(2026, 10, 4)},
     "check_out"),
    ({"room": "large"}, "room"),
    ({"check_in": date(2026, 10, 7), "check_out": date(2026, 10, 9)},
     "room"),
    ({"pet": "puppy"}, "pet"),
])
def test_clean_checks_business_rules(hotel, changes, field):
    """clean проверяет период, размер места, занятость и допуск питомца"""
    values = {"pet": hotel["barsik"], "room": hotel["small"],
              "check_in": date(2026, 12, 1), "check_out": date(2026, 12, 3)}
    for key, value in changes.items():
        values[key] = hotel[value] if isinstance(value, str) else value
    with pytest.raises(ValidationError) as error:
        Booking(**values).full_clean()
    assert field in error.value.message_dict


def test_clean_allows_free_room_and_cancelled_overlap(hotel):
    """Пересечение с отменённой бронью не мешает новой брони"""
    Booking(pet=hotel["barsik"], room=hotel["small"],
            check_in=date(2026, 11, 1),
            check_out=date(2026, 11, 3)).full_clean()


def test_statistics_counts_statuses(client, hotel):
    """Статистика показывает число броней каждого статуса"""
    Booking.objects.filter(pet=hotel["barsik"]).update(
        status=Booking.Status.COMPLETED
    )
    summary = client.get("/bookings/statistics/").context["summary"]
    assert (summary["active_count"], summary["completed_count"],
            summary["cancelled_count"]) == (1, 1, 1)
    assert summary["income"] == 7 * 800 + 7 * 1800


@pytest.fixture
def admin_client_logged(client, django_user_model):
    """Клиент, вошедший как суперпользователь"""
    django_user_model.objects.create_superuser("admin", "a@a.ru", "secret")
    client.login(username="admin", password="secret")
    return client


@pytest.mark.parametrize("url", [
    "/admin/", "/admin/rooms/room/", "/admin/users/user/",
    "/admin/pets/pet/", "/admin/bookings/booking/",
    "/admin/bookings/booking/add/",
])
def test_admin_pages_open(admin_client_logged, hotel, url):
    """Страницы административной панели открываются"""
    assert admin_client_logged.get(url).status_code == 200


def test_admin_search_is_case_insensitive(admin_client_logged, hotel):
    """Поиск в админке находит кириллицу в любом регистре"""
    response = admin_client_logged.get("/admin/bookings/booking/",
                                       {"q": "РЕКС"})
    assert response.context["cl"].result_count == 2


def test_admin_restore_skips_busy_room(admin_client_logged, hotel):
    """Возврат в активные пропускает бронь, если место уже занято"""
    cancelled = hotel["cancelled"]
    Booking.objects.create(pet=hotel["barsik"], room=hotel["small"],
                           check_in=date(2026, 11, 2),
                           check_out=date(2026, 11, 4))
    admin_client_logged.post("/admin/bookings/booking/", {
        "action": "restore_selected",
        "_selected_action": [cancelled.pk],
    })
    cancelled.refresh_from_db()
    assert cancelled.status == Booking.Status.CANCELLED


def test_room_slug_and_absolute_url(client, hotel):
    """Slug формируется транслитерацией, страница открывается по нему"""
    room = Room.objects.create(name="Вольер Люкс", size="малое",
                               price_per_night=900)
    assert room.slug == f"voler-liuks-{room.pk}"
    assert room.get_absolute_url() == f"/rooms/{room.slug}/"
    room.name = "Новое название"
    room.save()
    room.refresh_from_db()
    assert room.slug == f"voler-liuks-{room.pk}"
    response = client.get(room.get_absolute_url())
    assert response.context["room"] == room


def test_generated_room_size_follows_weight(hotel):
    """Размер места вычисляет база по весу и пересчитывает при изменении"""
    assert Pet.objects.get(pk=hotel["barsik"].pk).room_size == "малое"
    assert Pet.objects.filter(room_size="большое").get() == hotel["rex"]
    pet = hotel["barsik"]
    pet.weight_kg = 12
    pet.save()
    pet.refresh_from_db()
    assert pet.room_size == "среднее" == pet.required_room_size()
