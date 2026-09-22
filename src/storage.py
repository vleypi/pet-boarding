import json
from pathlib import Path

from src.constants import (
    BOOKINGS_FILE,
    ENCODING,
    JSON_INDENT,
    PETS_FILE,
    ROOMS_FILE,
    USERS_FILE,
)
from src.models import Booking, Pet, Room, User
from src.models.pets import find_pet_by_id
from src.models.rooms import find_room_by_id
from src.models.users import find_user_by_id


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


def report_skipped(path: Path, item: dict) -> None:
    """Сообщить о записи, для которой не найдены связанные данные"""
    print(
        f"Файл {path.name}: запись {item.get('id')} пропущена, "
        f"связанные данные не найдены"
    )


def load_users() -> list[User]:
    """Загрузить пользователей и создать объекты User"""
    return [User.from_data(item) for item in load_json(USERS_FILE)]


def save_users(users: list[User]) -> None:
    """Сохранить пользователей в файл"""
    save_json(USERS_FILE, [user.to_data() for user in users])


def load_rooms() -> list[Room]:
    """Загрузить места и создать объекты Room"""
    return [Room.from_data(item) for item in load_json(ROOMS_FILE)]


def save_rooms(rooms: list[Room]) -> None:
    """Сохранить места в файл"""
    save_json(ROOMS_FILE, [room.to_data() for room in rooms])


def load_pets(users: list[User]) -> list[Pet]:
    """Загрузить питомцев и связать каждого с объектом владельца"""
    pets = []
    for item in load_json(PETS_FILE):
        owner = find_user_by_id(users, item.get("owner_id"))
        if owner is None:
            report_skipped(PETS_FILE, item)
            continue
        pets.append(Pet.from_data(item, owner))
    return pets


def save_pets(pets: list[Pet]) -> None:
    """Сохранить питомцев в файл"""
    save_json(PETS_FILE, [pet.to_data() for pet in pets])


def load_bookings(pets: list[Pet], rooms: list[Room]) -> list[Booking]:
    """Загрузить бронирования и связать их с питомцами и местами"""
    bookings = []
    for item in load_json(BOOKINGS_FILE):
        pet = find_pet_by_id(pets, item.get("pet_id"))
        room = find_room_by_id(rooms, item.get("room_id"))
        if pet is None or room is None:
            report_skipped(BOOKINGS_FILE, item)
            continue
        bookings.append(Booking.from_data(item, pet, room))
    return bookings


def save_bookings(bookings: list[Booking]) -> None:
    """Сохранить бронирования в файл"""
    save_json(BOOKINGS_FILE, [booking.to_data() for booking in bookings])
