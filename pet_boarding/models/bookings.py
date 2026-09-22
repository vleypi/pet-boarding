from datetime import date
from typing import Optional

from pet_boarding.constants import STATUS_ACTIVE, STATUS_CANCELLED
from pet_boarding.exceptions import (
    InvalidPeriodError,
    PetNotAcceptedError,
    RoomNotAvailableError,
    RoomNotSuitableError,
)
from pet_boarding.models.common import count_nights, next_id
from pet_boarding.models.pets import Pet
from pet_boarding.models.rooms import Room


class Booking:
    """Бронирование места для питомца на период проживания"""

    def __init__(
        self,
        booking_id: int,
        pet: Pet,
        room: Room,
        check_in: date,
        check_out: date,
        is_cancelled: bool = False,
    ) -> None:
        """Создать бронирование"""
        self.id = booking_id
        self.pet = pet
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self._is_cancelled = is_cancelled

    def __str__(self) -> str:
        """Вернуть строковое представление бронирования"""
        return (
            f"Бронирование {self.id}: {self.pet.name}, {self.room.name}, "
            f"с {self.check_in} по {self.check_out}, {self.status}"
        )

    @property
    def is_cancelled(self) -> bool:
        """Признак отмены, изменяется только методом cancel"""
        return self._is_cancelled

    @property
    def status(self) -> str:
        """Текстовое состояние бронирования"""
        if self._is_cancelled:
            return STATUS_CANCELLED
        return STATUS_ACTIVE

    @property
    def nights(self) -> int:
        """Число суток проживания"""
        return count_nights(self.check_in, self.check_out)

    @property
    def cost(self) -> int:
        """Стоимость проживания по тарифу места"""
        return self.room.cost_for(self.check_in, self.check_out)

    def cancel(self) -> None:
        """Отменить бронирование"""
        self._is_cancelled = True

    def overlaps(self, check_in: date, check_out: date) -> bool:
        """Проверить, пересекается ли бронирование с периодом"""
        return self.check_in < check_out and check_in < self.check_out

    @classmethod
    def from_data(cls, data: dict, pet: Pet, room: Room) -> "Booking":
        """Создать бронирование из данных JSON и связанных объектов"""
        return cls(
            booking_id=data["id"],
            pet=pet,
            room=room,
            check_in=date.fromisoformat(data["check_in"]),
            check_out=date.fromisoformat(data["check_out"]),
            is_cancelled=data.get("is_cancelled", False),
        )

    def to_data(self) -> dict:
        """Вернуть данные бронирования для записи в JSON"""
        return {
            "id": self.id,
            "pet_id": self.pet.id,
            "room_id": self.room.id,
            "check_in": self.check_in.isoformat(),
            "check_out": self.check_out.isoformat(),
            "is_cancelled": self._is_cancelled,
        }


def find_booking_by_id(
    bookings: list[Booking],
    booking_id: int,
) -> Optional[Booking]:
    """Найти бронирование по идентификатору"""
    return next(
        (booking for booking in bookings if booking.id == booking_id),
        None,
    )


def is_room_available(
    bookings: list[Booking],
    room: Room,
    check_in: date,
    check_out: date,
) -> bool:
    """Проверить, свободно ли место на указанные даты"""
    for booking in bookings:
        if booking.is_cancelled or booking.room.id != room.id:
            continue
        if booking.overlaps(check_in, check_out):
            return False
    return True


def validate_period(check_in: date, check_out: date) -> None:
    """Проверить, что дата выезда позже даты заезда"""
    if check_out <= check_in:
        raise InvalidPeriodError("дата выезда должна быть позже даты заезда")


def get_booking_status(is_available: bool) -> str:
    """Вернуть текстовый статус места"""
    if is_available:
        return "Место свободно на эти даты"
    return "Место уже занято"


def create_booking(
    bookings: list[Booking],
    pet: Pet,
    room: Room,
    check_in: date,
    check_out: date,
) -> Booking:
    """Проверить условия, создать бронирование и добавить его в список"""
    validate_period(check_in, check_out)
    reason = pet.rejection_reason()
    if reason:
        raise PetNotAcceptedError(reason)
    if not room.is_suitable_for(pet):
        size = pet.required_room_size()
        raise RoomNotSuitableError(f"питомцу нужно {size} место")
    if not is_room_available(bookings, room, check_in, check_out):
        raise RoomNotAvailableError("место занято на эти даты")
    booking = Booking(next_id(bookings), pet, room, check_in, check_out)
    bookings.append(booking)
    return booking


def cancel_booking(bookings: list[Booking], booking_id: int) -> bool:
    """Отменить активное бронирование по идентификатору"""
    booking = find_booking_by_id(bookings, booking_id)
    if booking is None or booking.is_cancelled:
        return False
    booking.cancel()
    return True


def sort_bookings_by_date(bookings: list[Booking]) -> list[Booking]:
    """Вернуть бронирования, упорядоченные по дате заезда"""
    return sorted(bookings, key=lambda booking: booking.check_in)


def get_statistics(bookings: list[Booking]) -> dict:
    """Собрать статистику по бронированиям"""
    active = [booking for booking in bookings if not booking.is_cancelled]
    total_nights = 0
    total_income = 0
    for booking in active:
        total_nights += booking.nights
        total_income += booking.cost
    average_nights = 0.0
    if active:
        average_nights = round(total_nights / len(active), 1)
    return {
        "active": len(active),
        "cancelled": len(bookings) - len(active),
        "nights": total_nights,
        "income": total_income,
        "average_nights": average_nights,
    }
