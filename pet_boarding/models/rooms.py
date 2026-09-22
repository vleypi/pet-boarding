from datetime import date
from typing import Optional

from pet_boarding.constants import ROOM_SIZES
from pet_boarding.models.common import count_nights
from pet_boarding.models.pets import Pet


class Room:
    """Место в гостинице: вольер или комната определённого размера"""

    def __init__(
        self,
        room_id: int,
        name: str,
        size: str,
        price_per_night: int,
    ) -> None:
        """Создать место"""
        self.id = room_id
        self.name = name
        self.size = size
        self.price_per_night = price_per_night

    def __str__(self) -> str:
        """Вернуть строковое представление места"""
        return (
            f"{self.name}, {self.size} место, "
            f"{self.price_per_night} рублей в сутки"
        )

    def is_suitable_for(self, pet: Pet) -> bool:
        """Проверить, подходит ли место питомцу по размеру"""
        return self.size == pet.required_room_size()

    def cost_for(self, check_in: date, check_out: date) -> int:
        """Посчитать стоимость проживания в месте за период"""
        return count_nights(check_in, check_out) * self.price_per_night

    @classmethod
    def from_data(cls, data: dict) -> "Room":
        """Создать место из данных JSON"""
        return cls(
            room_id=data["id"],
            name=data["name"],
            size=data["size"],
            price_per_night=data["price_per_night"],
        )

    def to_data(self) -> dict:
        """Вернуть данные места для записи в JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "price_per_night": self.price_per_night,
        }


def find_room_by_id(rooms: list[Room], room_id: int) -> Optional[Room]:
    """Найти место по идентификатору"""
    return next((room for room in rooms if room.id == room_id), None)


def filter_rooms_for_pet(rooms: list[Room], pet: Pet) -> list[Room]:
    """Отобрать места, подходящие питомцу по размеру"""
    suitable = (room for room in rooms if room.is_suitable_for(pet))
    return list(suitable)


def sort_rooms_by_price(rooms: list[Room]) -> list[Room]:
    """Вернуть места, упорядоченные по тарифу"""
    return sorted(rooms, key=lambda room: room.price_per_night)


def count_by_size(rooms: list[Room]) -> dict[str, int]:
    """Посчитать количество мест каждого размера"""
    counters: dict[str, int] = {}
    for size in ROOM_SIZES:
        counters[size] = sum(1 for room in rooms if room.size == size)
    return counters
