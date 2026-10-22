import sqlite3
from contextlib import closing

import pytest

from db.database import (
    create_schema,
    fetch_all,
    fetch_one,
    get_connection,
    load_queries,
)
from db.import_json import (
    import_all,
    import_bookings,
    import_pets,
    import_rooms,
    import_users,
)
from src.constants import BOOKINGS_FILE, PETS_FILE, ROOMS_FILE, USERS_FILE
from src.storage import load_json

USERS = [{"id": 1, "name": "Анна", "phone": "+7 1", "role": "клиент"}]
ROOMS = [
    {"id": 1, "name": "Вольер", "size": "малое", "price_per_night": 800},
    {"id": 2, "name": "Апартаменты", "size": "большое",
     "price_per_night": 1800},
]
PETS = [
    {"id": 1, "name": "Барсик", "species": "кошка", "age_months": 18,
     "weight_kg": 4.5, "is_vaccinated": True, "owner_id": 1},
    {"id": 2, "name": "Мухтар", "species": "собака", "age_months": 8,
     "weight_kg": 30.0, "is_vaccinated": False, "owner_id": 1},
]
BOOKINGS = [
    {"id": 1, "pet_id": 1, "room_id": 1, "check_in": "2026-10-01",
     "check_out": "2026-10-08", "is_cancelled": False},
    {"id": 2, "pet_id": 1, "room_id": 1, "check_in": "2026-11-01",
     "check_out": "2026-11-03", "is_cancelled": False},
    {"id": 3, "pet_id": 1, "room_id": 2, "check_in": "2026-10-01",
     "check_out": "2026-10-08", "is_cancelled": True},
]

PARAMS = {
    "rooms_by_size": ("малое",),
    "available_rooms": ("2026-10-08", "2026-10-03", "", ""),
    "popular_rooms": (2,),
    "upcoming_check_ins": ("2026-01-01", 3),
}


@pytest.fixture
def db_path(tmp_path):
    """Временная база с тестовыми данными"""
    path = tmp_path / "test.sqlite"
    with closing(get_connection(path)) as conn:
        create_schema(conn)
        import_users(conn, USERS)
        import_rooms(conn, ROOMS)
        import_pets(conn, PETS)
        import_bookings(conn, BOOKINGS)
        conn.commit()
    return path


def test_schema_creates_tables_and_foreign_keys(db_path):
    """Схема создаёт четыре таблицы и внешние ключи броней"""
    with closing(get_connection(db_path)) as conn:
        tables = {row["name"] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )}
        keys = {row["table"] for row in conn.execute(
            "PRAGMA foreign_key_list(bookings)"
        )}
    assert tables == {"users", "rooms", "pets", "bookings"}
    assert keys == {"pets", "rooms"}


def test_foreign_key_is_enforced(db_path):
    """Бронь с несуществующим питомцем не сохраняется"""
    with closing(get_connection(db_path)) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO bookings (pet_id, room_id, check_in, check_out) "
                "VALUES (?, ?, ?, ?)",
                (99, 1, "2026-12-01", "2026-12-02"),
            )


def test_queries_file_has_enough_queries():
    """В файле запросов не меньше десяти именованных запросов"""
    assert len(load_queries()) >= 10


@pytest.mark.parametrize("name", sorted(load_queries()))
def test_every_query_runs(db_path, name):
    """Каждый запрос из файла выполняется без ошибок"""
    fetch_all(name, PARAMS.get(name, ()), db_path)


def test_available_rooms_skip_overlaps_only(db_path):
    """Занятое место исключается, отменённая бронь место не блокирует"""
    rooms = fetch_all("available_rooms", PARAMS["available_rooms"], db_path)
    assert [room["name"] for room in rooms] == ["Апартаменты"]
    rooms = fetch_all(
        "available_rooms", ("2026-10-10", "2026-10-08", "", ""), db_path
    )
    assert len(rooms) == 2


def test_having_filters_groups(db_path):
    """HAVING оставляет только места с нужным числом броней"""
    assert len(fetch_all("popular_rooms", (2,), db_path)) == 1
    assert fetch_all("popular_rooms", (3,), db_path) == []


def test_income_counts_only_active(db_path):
    """Выручка считается только по активным броням"""
    summary = fetch_one("income_summary", (), db_path)
    assert summary["bookings_count"] == 2
    assert summary["income"] == 7 * 800 + 2 * 800


def test_parameters_are_not_executed_as_sql(db_path):
    """Подстановка через параметр не меняет смысл запроса"""
    rooms = fetch_all("rooms_by_size", ("' OR 1 = 1 --",), db_path)
    assert rooms == []


def test_import_matches_json_files(tmp_path):
    """Число записей в таблицах совпадает с JSON-файлами проекта"""
    with closing(get_connection(tmp_path / "full.sqlite")) as conn:
        create_schema(conn)
        counts = import_all(conn)
        conn.commit()
    assert counts == {
        "users": len(load_json(USERS_FILE)),
        "rooms": len(load_json(ROOMS_FILE)),
        "pets": len(load_json(PETS_FILE)),
        "bookings": len(load_json(BOOKINGS_FILE)),
    }
