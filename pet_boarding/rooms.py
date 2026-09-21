"""Функции работы с местами гостиницы"""

from pet_boarding.constants import ROOM_SIZES


def get_room(rooms: dict[int, dict], room_id: int) -> dict:
    """Вернуть место по идентификатору"""
    if room_id not in rooms:
        raise KeyError(f"место с номером {room_id} не найдено")
    return rooms[room_id]


def get_room_price(rooms: dict[int, dict], room_id: int) -> int:
    """Вернуть тариф места за сутки"""
    return get_room(rooms, room_id)["price_per_night"]


def filter_rooms_by_size(rooms: dict[int, dict], size: str) -> list[dict]:
    """Отобрать места указанного размера"""
    suitable = (room for room in rooms.values() if room["size"] == size)
    return list(suitable)


def sort_rooms_by_price(rooms: dict[int, dict]) -> list[dict]:
    """Вернуть места, упорядоченные по тарифу"""
    return sorted(rooms.values(), key=lambda room: room["price_per_night"])


def count_by_size(rooms: dict[int, dict]) -> dict[str, int]:
    """Посчитать количество мест каждого размера"""
    counters = {}
    for size in ROOM_SIZES:
        counters[size] = len(filter_rooms_by_size(rooms, size))
    return counters
