import sqlite3
from contextlib import closing

from db.database import create_schema, get_connection
from src.constants import BOOKINGS_FILE, PETS_FILE, ROOMS_FILE, USERS_FILE
from src.storage import load_json

CLEAR_STATEMENTS = (
    "DELETE FROM bookings",
    "DELETE FROM pets",
    "DELETE FROM rooms",
    "DELETE FROM users",
)


def import_users(conn: sqlite3.Connection, users: list[dict]) -> int:
    """Перенести пользователей в таблицу users"""
    conn.executemany(
        "INSERT INTO users (id, name, phone, role) VALUES (?, ?, ?, ?)",
        [(u["id"], u["name"], u["phone"], u["role"]) for u in users],
    )
    return len(users)


def import_rooms(conn: sqlite3.Connection, rooms: list[dict]) -> int:
    """Перенести места в таблицу rooms"""
    conn.executemany(
        "INSERT INTO rooms (id, name, size, price_per_night) "
        "VALUES (?, ?, ?, ?)",
        [
            (r["id"], r["name"], r["size"], r["price_per_night"])
            for r in rooms
        ],
    )
    return len(rooms)


def import_pets(conn: sqlite3.Connection, pets: list[dict]) -> int:
    """Перенести питомцев в таблицу pets"""
    conn.executemany(
        "INSERT INTO pets (id, name, species, age_months, weight_kg, "
        "is_vaccinated, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (
                p["id"],
                p["name"],
                p["species"],
                p["age_months"],
                p["weight_kg"],
                int(p["is_vaccinated"]),
                p["owner_id"],
            )
            for p in pets
        ],
    )
    return len(pets)


def import_bookings(conn: sqlite3.Connection, bookings: list[dict]) -> int:
    """Перенести бронирования в таблицу bookings"""
    conn.executemany(
        "INSERT INTO bookings (id, pet_id, room_id, check_in, check_out, "
        "is_cancelled) VALUES (?, ?, ?, ?, ?, ?)",
        [
            (
                b["id"],
                b["pet_id"],
                b["room_id"],
                b["check_in"],
                b["check_out"],
                int(b.get("is_cancelled", False)),
            )
            for b in bookings
        ],
    )
    return len(bookings)


def import_all(conn: sqlite3.Connection) -> dict[str, int]:
    """Очистить таблицы и перенести все данные из JSON в связанном порядке"""
    for statement in CLEAR_STATEMENTS:
        conn.execute(statement)
    return {
        "users": import_users(conn, load_json(USERS_FILE)),
        "rooms": import_rooms(conn, load_json(ROOMS_FILE)),
        "pets": import_pets(conn, load_json(PETS_FILE)),
        "bookings": import_bookings(conn, load_json(BOOKINGS_FILE)),
    }


def main() -> None:
    """Создать схему и перенести данные, при ошибке откатить изменения"""
    with closing(get_connection()) as conn:
        create_schema(conn)
        try:
            counts = import_all(conn)
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise
    for table, count in counts.items():
        print(f"{table}: {count}")


if __name__ == "__main__":
    main()
