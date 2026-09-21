"""Функции работы с бронированиями"""

from datetime import date

from pet_boarding.rooms import get_room_price


def booking_period(booking: dict) -> tuple[date, date]:
    """Вернуть даты заезда и выезда бронирования"""
    return (
        date.fromisoformat(booking["check_in"]),
        date.fromisoformat(booking["check_out"]),
    )


def count_nights(check_in: date, check_out: date) -> int:
    """Посчитать число суток проживания"""
    return (check_out - check_in).days


def periods_overlap(
    first_in: date,
    first_out: date,
    second_in: date,
    second_out: date,
) -> bool:
    """Проверить, пересекаются ли два периода проживания"""
    return first_in < second_out and second_in < first_out


def is_room_available(
    bookings: list[dict],
    room_id: int,
    check_in: date,
    check_out: date,
) -> bool:
    """Проверить, свободно ли место на указанные даты"""
    for booking in bookings:
        if booking["room_id"] != room_id:
            continue
        booked_in, booked_out = booking_period(booking)
        if periods_overlap(check_in, check_out, booked_in, booked_out):
            return False
    return True


def get_booking_status(is_available: bool) -> str:
    """Вернуть текстовый статус места"""
    if is_available:
        return "Место свободно на эти даты"
    return "Место уже занято"


def calculate_boarding_cost(
    check_in: date,
    check_out: date,
    price_per_night: int,
) -> int:
    """Посчитать стоимость проживания за весь срок"""
    return count_nights(check_in, check_out) * price_per_night


def next_booking_id(bookings: list[dict]) -> int:
    """Вернуть свободный идентификатор бронирования"""
    if not bookings:
        return 1
    return max(booking["id"] for booking in bookings) + 1


def create_booking(
    bookings: list[dict],
    pet_id: int,
    room_id: int,
    check_in: date,
    check_out: date,
) -> dict:
    """Создать бронирование и добавить его в список"""
    if check_out <= check_in:
        raise ValueError("дата выезда должна быть позже даты заезда")
    if not is_room_available(bookings, room_id, check_in, check_out):
        raise ValueError("место занято на эти даты")
    booking = {
        "id": next_booking_id(bookings),
        "pet_id": pet_id,
        "room_id": room_id,
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
    }
    bookings.append(booking)
    return booking


def cancel_booking(bookings: list[dict], booking_id: int) -> bool:
    """Отменить бронирование по идентификатору"""
    for index, booking in enumerate(bookings):
        if booking["id"] == booking_id:
            del bookings[index]
            return True
    return False


def find_bookings_by_pet(bookings: list[dict], pet_id: int) -> list[dict]:
    """Найти бронирования питомца"""
    return [booking for booking in bookings if booking["pet_id"] == pet_id]


def sort_bookings_by_date(bookings: list[dict]) -> list[dict]:
    """Вернуть бронирования, упорядоченные по дате заезда"""
    return sorted(bookings, key=lambda booking: booking["check_in"])


def get_statistics(bookings: list[dict], rooms: dict[int, dict]) -> dict:
    """Собрать статистику по бронированиям"""
    total_nights = 0
    total_income = 0
    for booking in bookings:
        check_in, check_out = booking_period(booking)
        total_nights += count_nights(check_in, check_out)
        total_income += calculate_boarding_cost(
            check_in,
            check_out,
            get_room_price(rooms, booking["room_id"]),
        )
    average_nights = 0.0
    if bookings:
        average_nights = round(total_nights / len(bookings), 1)
    return {
        "bookings": len(bookings),
        "nights": total_nights,
        "income": total_income,
        "average_nights": average_nights,
    }
