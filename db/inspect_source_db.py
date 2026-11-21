import sqlite3
from contextlib import closing

from db.database import get_connection
from src.constants import DB_FILE

INTEGRITY_CHECKS = {
    "питомцы без владельца": (
        "SELECT COUNT(*) FROM pets "
        "WHERE owner_id NOT IN (SELECT id FROM users)"
    ),
    "бронирования без питомца": (
        "SELECT COUNT(*) FROM bookings "
        "WHERE pet_id NOT IN (SELECT id FROM pets)"
    ),
    "бронирования без места": (
        "SELECT COUNT(*) FROM bookings "
        "WHERE room_id NOT IN (SELECT id FROM rooms)"
    ),
    "неверный признак отмены": (
        "SELECT COUNT(*) FROM bookings WHERE is_cancelled NOT IN (0, 1)"
    ),
    "даты не в формате ГГГГ-ММ-ДД": (
        "SELECT COUNT(*) FROM bookings "
        "WHERE date(check_in) IS NOT check_in "
        "OR date(check_out) IS NOT check_out"
    ),
}


def table_names(conn: sqlite3.Connection) -> list[str]:
    """Вернуть имена пользовательских таблиц базы"""
    rows = conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [row["name"] for row in rows]


def print_table(conn: sqlite3.Connection, table: str) -> None:
    """Вывести столбцы таблицы и число записей в ней"""
    print(f"\nТаблица: {table}")
    for column in conn.execute(f'PRAGMA table_info("{table}")'):
        print(
            f"  {column['name']}: {column['type']}, "
            f"NOT NULL={column['notnull']}, PRIMARY KEY={column['pk']}"
        )
    count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    print(f"  записей: {count}")


def print_integrity(conn: sqlite3.Connection) -> None:
    """Вывести число записей, нарушающих связи и форматы"""
    print("\nПроверка данных:")
    for title, query in INTEGRITY_CHECKS.items():
        print(f"  {title}: {conn.execute(query).fetchone()[0]}")


def main() -> None:
    """Вывести структуру исходной базы ПР7 без изменения данных"""
    if not DB_FILE.exists():
        raise FileNotFoundError(f"исходная база не найдена: {DB_FILE}")
    with closing(get_connection(DB_FILE)) as conn:
        for table in table_names(conn):
            print_table(conn, table)
        print_integrity(conn)


if __name__ == "__main__":
    main()
