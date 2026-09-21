import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ROOMS_FILE = DATA_DIR / "rooms.json"
PETS_FILE = DATA_DIR / "pets.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"


def load_json(path: Path) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {path.name} не найден, данные пустые")
        return []
    except json.JSONDecodeError:
        print(f"Файл {path.name} повреждён, данные пустые")
        return []


def save_json(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.write("\n")


def load_rooms() -> dict[int, dict]:
    return {room["id"]: room for room in load_json(ROOMS_FILE)}


def save_rooms(rooms: dict[int, dict]) -> None:
    save_json(ROOMS_FILE, list(rooms.values()))


def load_pets() -> dict[int, dict]:
    return {pet["id"]: pet for pet in load_json(PETS_FILE)}


def save_pets(pets: dict[int, dict]) -> None:
    save_json(PETS_FILE, list(pets.values()))


def load_bookings() -> list[dict]:
    return load_json(BOOKINGS_FILE)


def save_bookings(bookings: list[dict]) -> None:
    save_json(BOOKINGS_FILE, bookings)
