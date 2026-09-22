from datetime import date

import pytest

from pet_boarding.bookings import (
    calculate_boarding_cost,
    cancel_booking,
    create_booking,
    is_room_available,
)


def test_free_room_is_available():
    """Место без бронирований свободно"""
    bookings = []
    assert is_room_available(
        bookings, 1, date(2026, 10, 1), date(2026, 10, 8)
    )


def test_booked_room_is_not_available():
    """Место занято, если даты пересекаются с бронированием"""
    bookings = []
    create_booking(bookings, 1, 1, date(2026, 10, 1), date(2026, 10, 8))
    assert not is_room_available(
        bookings, 1, date(2026, 10, 3), date(2026, 10, 5)
    )


def test_room_is_free_on_checkout_day():
    """Место свободно в день выезда предыдущего питомца"""
    bookings = []
    create_booking(bookings, 1, 1, date(2026, 10, 1), date(2026, 10, 8))
    assert is_room_available(
        bookings, 1, date(2026, 10, 8), date(2026, 10, 12)
    )


def test_calculate_boarding_cost():
    """Стоимость равна числу суток, умноженному на тариф"""
    cost = calculate_boarding_cost(
        date(2026, 10, 1), date(2026, 10, 8), 1200
    )
    assert cost == 8400


def test_create_booking_rejects_wrong_dates():
    """Бронирование с выездом раньше заезда не создаётся"""
    bookings = []
    with pytest.raises(ValueError):
        create_booking(bookings, 1, 1, date(2026, 10, 8), date(2026, 10, 1))


def test_cancel_booking_removes_it():
    """Отменённое бронирование исчезает из списка"""
    bookings = []
    booking = create_booking(
        bookings, 1, 1, date(2026, 10, 1), date(2026, 10, 8)
    )
    assert cancel_booking(bookings, booking["id"])
    assert bookings == []


def test_cancel_unknown_booking_returns_false():
    """Отмена несуществующего бронирования возвращает False"""
    assert not cancel_booking([], 99)
