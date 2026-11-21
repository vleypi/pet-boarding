import sqlite3
from pathlib import Path

from src.constants import DB_FILE, ENCODING

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
SCHEMA_FILE = SQL_DIR / "schema.sql"


def get_connection(path: Path = DB_FILE) -> sqlite3.Connection:
    """Открыть базу с проверкой внешних ключей и доступом к полям по именам"""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Создать таблицы по файлу sql/schema.sql"""
    conn.executescript(SCHEMA_FILE.read_text(encoding=ENCODING))
