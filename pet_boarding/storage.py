"""Чтение и запись данных проекта в файлах формата JSON"""

import json
from pathlib import Path

from pet_boarding.constants import (
    BOOKINGS_FILE,
    ENCODING,
    JSON_INDENT,
    PETS_FILE,
    ROOMS_FILE,
)


def load_json(path: Path) -> list[dict]:
    """Прочитать список словарей из JSON-файла"""
    try:
        with open(path, encoding=ENCODING) as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {path.name} не найден, данные пустые")
        return []
    except json.JSONDecodeError:
        print(f"Файл {path.name} повреждён, данные пустые")
        return []


def save_json(path: Path, data: list[dict]) -> None:
    """Записать список словарей в JSON-файл"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding=ENCODING) as file:
        json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)
        file.write("\n")


def load_rooms() -> dict[int, dict]:
    """Загрузить места и вернуть словарь, ключ это идентификатор"""
    return {room["id"]: room for room in load_json(ROOMS_FILE)}


def save_rooms(rooms: dict[int, dict]) -> None:
    """Сохранить места в файл"""
    save_json(ROOMS_FILE, list(rooms.values()))


def load_pets() -> dict[int, dict]:
    """Загрузить питомцев и вернуть словарь, ключ это идентификатор"""
    return {pet["id"]: pet for pet in load_json(PETS_FILE)}


def save_pets(pets: dict[int, dict]) -> None:
    """Сохранить питомцев в файл"""
    save_json(PETS_FILE, list(pets.values()))


def load_bookings() -> list[dict]:
    """Загрузить бронирования и вернуть список"""
    return load_json(BOOKINGS_FILE)


def save_bookings(bookings: list[dict]) -> None:
    """Сохранить бронирования в файл"""
    save_json(BOOKINGS_FILE, bookings)
