from datetime import date

import pytest

from pet_boarding.constants import STATUS_ACTIVE, STATUS_CANCELLED
from pet_boarding.exceptions import (
    BookingError,
    InvalidPeriodError,
    PetNotAcceptedError,
    RoomNotAvailableError,
    RoomNotSuitableError,
)
from pet_boarding.models import Booking, Pet
from pet_boarding.models.bookings import (
    cancel_booking,
    create_booking,
    get_statistics,
    is_room_available,
)

OCT_1 = date(2026, 10, 1)
OCT_3 = date(2026, 10, 3)
OCT_5 = date(2026, 10, 5)
OCT_8 = date(2026, 10, 8)
OCT_12 = date(2026, 10, 12)


def test_booking_links_pet_and_room(cat, small_room):
    """Бронирование хранит сами объекты питомца и места"""
    booking = create_booking([], cat, small_room, OCT_1, OCT_8)
    assert booking.pet is cat
    assert booking.room is small_room
    assert booking.pet.owner.name == "Иванова Анна"


def test_booking_properties(cat, small_room):
    """Статус, число суток и стоимость читаются как свойства"""
    booking = create_booking([], cat, small_room, OCT_1, OCT_8)
    assert booking.status == STATUS_ACTIVE
    assert booking.nights == 7
    assert booking.cost == 5600


def test_is_cancelled_cannot_be_assigned(cat, small_room):
    """Признак отмены нельзя изменить присваиванием"""
    booking = create_booking([], cat, small_room, OCT_1, OCT_8)
    with pytest.raises(AttributeError):
        booking.is_cancelled = True


def test_free_room_is_available(small_room):
    """Место без бронирований свободно"""
    assert is_room_available([], small_room, OCT_1, OCT_8)


def test_second_active_booking_forbidden(cat, small_room):
    """Второе активное бронирование на пересекающиеся даты запрещено"""
    bookings = []
    create_booking(bookings, cat, small_room, OCT_1, OCT_8)
    assert not is_room_available(bookings, small_room, OCT_3, OCT_5)
    with pytest.raises(RoomNotAvailableError):
        create_booking(bookings, cat, small_room, OCT_3, OCT_5)


def test_room_is_free_on_checkout_day(cat, small_room):
    """Место свободно в день выезда предыдущего питомца"""
    bookings = []
    create_booking(bookings, cat, small_room, OCT_1, OCT_8)
    assert is_room_available(bookings, small_room, OCT_8, OCT_12)


def test_cancelled_booking_frees_room(cat, small_room):
    """После отмены место снова можно забронировать на те же даты"""
    bookings = []
    first = create_booking(bookings, cat, small_room, OCT_1, OCT_8)
    first.cancel()
    second = create_booking(bookings, cat, small_room, OCT_1, OCT_8)
    assert second.status == STATUS_ACTIVE


def test_cancel_keeps_booking_in_list(cat, small_room):
    """Отменённое бронирование остаётся в списке со статусом отмены"""
    bookings = []
    booking = create_booking(bookings, cat, small_room, OCT_1, OCT_8)
    assert cancel_booking(bookings, booking.id)
    assert bookings == [booking]
    assert booking.status == STATUS_CANCELLED


def test_cancel_twice_or_unknown_returns_false(cat, small_room):
    """Повторная отмена и отмена несуществующей брони возвращают False"""
    bookings = []
    booking = create_booking(bookings, cat, small_room, OCT_1, OCT_8)
    cancel_booking(bookings, booking.id)
    assert not cancel_booking(bookings, booking.id)
    assert not cancel_booking(bookings, 99)


def test_create_booking_rejects_wrong_dates(cat, small_room):
    """Бронирование с выездом раньше заезда не создаётся"""
    with pytest.raises(InvalidPeriodError):
        create_booking([], cat, small_room, OCT_8, OCT_1)


def test_create_booking_rejects_unaccepted_pet(owner, small_room):
    """Питомца без прививок забронировать нельзя"""
    pet = Pet(3, "Мухтар", "собака", 8, 4.0, False, owner)
    with pytest.raises(PetNotAcceptedError):
        create_booking([], pet, small_room, OCT_1, OCT_8)


def test_create_booking_rejects_unsuitable_room(dog, small_room):
    """Крупную собаку нельзя поселить в малое место"""
    with pytest.raises(RoomNotSuitableError):
        create_booking([], dog, small_room, OCT_1, OCT_8)


def test_booking_errors_share_base_class(dog, small_room):
    """Любую ошибку бронирования можно перехватить через BookingError"""
    with pytest.raises(BookingError):
        create_booking([], dog, small_room, OCT_1, OCT_8)


def test_booking_restored_from_data(cat, small_room):
    """Бронирование восстанавливается из JSON вместе с признаком отмены"""
    booking = create_booking([], cat, small_room, OCT_1, OCT_8)
    booking.cancel()
    restored = Booking.from_data(booking.to_data(), cat, small_room)
    assert restored.to_data() == booking.to_data()
    assert restored.is_cancelled


def test_statistics_counts_only_active_income(
    cat,
    dog,
    small_room,
    large_room,
):
    """Выручка считается только по активным бронированиям"""
    bookings = []
    create_booking(bookings, cat, small_room, OCT_1, OCT_8)
    cancelled = create_booking(bookings, dog, large_room, OCT_1, OCT_3)
    cancelled.cancel()
    stats = get_statistics(bookings)
    assert stats["active"] == 1
    assert stats["cancelled"] == 1
    assert stats["income"] == 5600
