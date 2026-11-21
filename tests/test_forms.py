from datetime import date, timedelta

import pytest
from django.test import Client
from django.utils import timezone

from bookings.forms import BookingFilterForm, BookingForm
from bookings.models import Booking
from pets.models import Pet
from rooms.models import Room
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def data():
    """Владелец, кошка, щенок без прививок, два места и активная бронь"""
    owner = User.objects.create(name="Иванова Анна", phone="+7 1")
    cat = Pet.objects.create(name="Барсик", species="кошка", age_months=18,
                             weight_kg=4.5, is_vaccinated=True, owner=owner)
    puppy = Pet.objects.create(name="Пушок", species="собака", age_months=2,
                               weight_kg=3.0, is_vaccinated=False,
                               owner=owner)
    small = Room.objects.create(name="Вольер 1", size="малое",
                                price_per_night=800)
    large = Room.objects.create(name="Апартаменты 1", size="большое",
                                price_per_night=1800)
    start = timezone.localdate() + timedelta(days=10)
    booking = Booking.objects.create(pet=cat, room=small, check_in=start,
                                     check_out=start + timedelta(days=3))
    return {"cat": cat, "puppy": puppy, "small": small, "large": large,
            "start": start, "booking": booking}


def form_data(pet, room, check_in, nights=2):
    """Данные POST для формы бронирования"""
    return {"pet": pet.pk, "room": room.pk,
            "check_in": check_in.isoformat(),
            "check_out": (check_in + timedelta(days=nights)).isoformat()}


def test_filter_form_valid_and_defaults(data):
    """Пустая форма фильтров корректна, сортировка по умолчанию"""
    form = BookingFilterForm({})
    assert form.is_valid()
    assert form.filters()["sort"] == "check_in"


def test_filter_form_converts_values(data):
    """Форма превращает строки GET в дату и объект места"""
    form = BookingFilterForm({"room": data["small"].pk,
                              "date_from": "2026-12-01", "q": "  барс "})
    assert form.is_valid()
    assert form.cleaned_data["room"] == data["small"]
    assert form.cleaned_data["date_from"] == date(2026, 12, 1)
    assert form.cleaned_data["q"] == "барс"


@pytest.mark.parametrize("params, field", [
    ({"date_from": "завтра"}, "date_from"),
    ({"room": "999"}, "room"),
    ({"status": "deleted"}, "status"),
    ({"date_from": "2027-01-10", "date_to": "2027-01-01"}, "date_to"),
])
def test_filter_form_errors_skip_only_bad_fields(data, params, field):
    """Неверное поле попадает в ошибки, остальные фильтры работают"""
    form = BookingFilterForm(dict(params, size="малое"))
    assert not form.is_valid()
    assert field in form.errors
    filters = form.filters()
    assert filters["size"] == "малое"
    assert not filters.get(field)


def test_booking_form_new_has_initial_dates(data):
    """Пустая форма предлагает заезд сегодня и выезд завтра"""
    form = BookingForm()
    today = timezone.localdate()
    assert form.initial["check_in"] == today
    assert form.initial["check_out"] == today + timedelta(days=1)


def test_booking_form_rejects_past_date(data):
    """Заезд в прошлом не принимается"""
    yesterday = timezone.localdate() - timedelta(days=1)
    form = BookingForm(form_data(data["cat"], data["small"], yesterday))
    assert not form.is_valid()
    assert "check_in" in form.errors


@pytest.mark.parametrize("pet, room, shift, field", [
    ("cat", "small", 1, "room"),
    ("cat", "large", 30, "room"),
    ("puppy", "small", 30, "pet"),
])
def test_booking_form_business_rules(data, pet, room, shift, field):
    """Занятое место, неподходящий размер и недопуск питомца"""
    check_in = data["start"] + timedelta(days=shift)
    form = BookingForm(form_data(data[pet], data[room], check_in))
    assert not form.is_valid()
    assert field in form.errors


def test_booking_form_check_out_before_check_in(data):
    """Выезд раньше заезда даёт ошибку поля выезда"""
    form = BookingForm(form_data(data["cat"], data["small"],
                                 data["start"] + timedelta(days=30), -1))
    assert not form.is_valid()
    assert "check_out" in form.errors


def test_create_view_get_and_post(client, data):
    """GET показывает форму, POST создаёт бронь и переходит к ней"""
    response = client.get("/bookings/create/",
                          {"room": data["small"].slug})
    assert response.status_code == 200
    assert response.context["form"].initial["room"] == data["small"]
    check_in = data["start"] + timedelta(days=20)
    response = client.post("/bookings/create/",
                           form_data(data["cat"], data["small"], check_in))
    booking = Booking.objects.get(check_in=check_in)
    assert response.status_code == 302
    assert response["Location"] == booking.get_absolute_url()
    assert booking.status == Booking.Status.ACTIVE


def test_create_view_shows_busy_error(client, data):
    """Занятое место выводится ошибкой, бронь не создаётся"""
    response = client.post("/bookings/create/", form_data(
        data["cat"], data["small"], data["start"] + timedelta(days=1)))
    assert response.status_code == 200
    assert "Место уже занято на эти даты" in response.content.decode()
    assert Booking.objects.count() == 1


def test_update_view_excludes_itself_from_busy_check(client, data):
    """Своя бронь не мешает сдвинуть даты внутри того же периода"""
    booking = data["booking"]
    response = client.post(f"/bookings/{booking.pk}/edit/", form_data(
        data["cat"], data["small"], data["start"] + timedelta(days=1)))
    assert response.status_code == 302
    booking.refresh_from_db()
    assert booking.check_in == data["start"] + timedelta(days=1)


def test_cancel_view_post_only(client, data):
    """Отмена только через POST, повторная отмена даёт 404"""
    booking = data["booking"]
    url = f"/bookings/{booking.pk}/cancel/"
    assert client.get(url).status_code == 405
    assert client.post(url).status_code == 302
    booking.refresh_from_db()
    assert booking.status == Booking.Status.CANCELLED
    assert client.post(url).status_code == 404
    assert client.get(f"/bookings/{booking.pk}/edit/").status_code == 404


def test_cancelled_booking_frees_room(client, data):
    """После отмены место можно забронировать на те же даты"""
    client.post(f"/bookings/{data['booking'].pk}/cancel/")
    form = BookingForm(form_data(data["cat"], data["small"], data["start"]))
    assert form.is_valid()


def test_csrf_is_required(data):
    """POST без CSRF-токена отклоняется"""
    strict = Client(enforce_csrf_checks=True)
    response = strict.post(f"/bookings/{data['booking'].pk}/cancel/")
    assert response.status_code == 403


def image_file(name="room.png", size=(40, 30)):
    """Небольшое PNG-изображение для загрузки"""
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    buffer = BytesIO()
    Image.new("RGB", size, (200, 120, 60)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(),
                              content_type="image/png")


def test_room_photo_upload(client, data, settings, tmp_path):
    """Фото сохраняется в MEDIA_ROOT и выводится на странице места"""
    settings.MEDIA_ROOT = tmp_path
    room = data["small"]
    url = f"/rooms/{room.slug}/photo/"
    assert client.get(url).status_code == 200
    response = client.post(url, {"photo": image_file()})
    assert response.status_code == 302
    room.refresh_from_db()
    assert room.photo.name.startswith("rooms/")
    assert (tmp_path / room.photo.name).exists()
    page = client.get(room.get_absolute_url()).content.decode()
    assert room.photo.url in page


@pytest.mark.parametrize("upload, message", [
    (None, "Выберите файл изображения"),
    ("text", "Загрузите правильное изображение"),
    ("big", "Файл больше 2 МБ"),
])
def test_room_photo_validation(client, data, settings, tmp_path, upload,
                               message, monkeypatch):
    """Пустая форма, не изображение и слишком большой файл отклоняются"""
    from django.core.files.uploadedfile import SimpleUploadedFile

    settings.MEDIA_ROOT = tmp_path
    files = {}
    if upload == "text":
        files["photo"] = SimpleUploadedFile("a.png", b"not an image",
                                            content_type="image/png")
    if upload == "big":
        monkeypatch.setattr("rooms.forms.MAX_PHOTO_SIZE", 10)
        files["photo"] = image_file()
    response = client.post(f"/rooms/{data['small'].slug}/photo/", files)
    assert response.status_code == 200
    assert message in response.content.decode()
