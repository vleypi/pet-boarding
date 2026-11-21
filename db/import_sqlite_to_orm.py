import os
import sqlite3
from contextlib import closing
from datetime import date

import django

from db.database import get_connection
from src.constants import DB_FILE


def read_rows(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    """Прочитать все строки таблицы исходной базы по порядку id"""
    return conn.execute(f'SELECT * FROM "{table}" ORDER BY id').fetchall()


def import_all(conn: sqlite3.Connection) -> dict[str, int]:
    """Очистить таблицы ORM и перенести данные с прежними id атомарно"""
    from django.db import transaction

    from bookings.models import Booking
    from pets.models import Pet
    from rooms.models import Room
    from users.models import User

    with transaction.atomic():
        for model in (Booking, Pet, Room, User):
            model.objects.all().delete()
        users = User.objects.bulk_create(
            User(id=row["id"], name=row["name"], phone=row["phone"],
                 role=row["role"])
            for row in read_rows(conn, "users")
        )
        rooms = Room.objects.bulk_create(
            Room(id=row["id"], name=row["name"], size=row["size"],
                 price_per_night=row["price_per_night"])
            for row in read_rows(conn, "rooms")
        )
        pets = Pet.objects.bulk_create(
            Pet(id=row["id"], name=row["name"], species=row["species"],
                age_months=row["age_months"], weight_kg=row["weight_kg"],
                is_vaccinated=bool(row["is_vaccinated"]),
                owner_id=row["owner_id"])
            for row in read_rows(conn, "pets")
        )
        bookings = Booking.objects.bulk_create(
            Booking(id=row["id"], pet_id=row["pet_id"],
                    room_id=row["room_id"],
                    check_in=date.fromisoformat(row["check_in"]),
                    check_out=date.fromisoformat(row["check_out"]),
                    is_cancelled=bool(row["is_cancelled"]))
            for row in read_rows(conn, "bookings")
        )
    return {
        "users": len(users),
        "rooms": len(rooms),
        "pets": len(pets),
        "bookings": len(bookings),
    }


def main() -> None:
    """Перенести данные из базы ПР7 в базу Django через ORM"""
    if not DB_FILE.exists():
        raise FileNotFoundError(f"исходная база не найдена: {DB_FILE}")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    with closing(get_connection(DB_FILE)) as conn:
        counts = import_all(conn)
    for table, count in counts.items():
        print(f"{table}: {count}")


if __name__ == "__main__":
    main()
