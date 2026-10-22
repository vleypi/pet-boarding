import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Optional

from src.constants import DB_FILE, ENCODING

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
SCHEMA_FILE = SQL_DIR / "schema.sql"
QUERIES_FILE = SQL_DIR / "queries.sql"
QUERY_NAME_MARK = "-- name:"


def get_connection(path: Path = DB_FILE) -> sqlite3.Connection:
    """Открыть базу с проверкой внешних ключей и доступом к полям по именам"""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Создать таблицы по файлу sql/schema.sql"""
    conn.executescript(SCHEMA_FILE.read_text(encoding=ENCODING))


def load_queries() -> dict[str, str]:
    """Прочитать именованные запросы из файла sql/queries.sql"""
    queries: dict[str, str] = {}
    name: Optional[str] = None
    lines: list[str] = []
    for line in QUERIES_FILE.read_text(encoding=ENCODING).splitlines():
        if line.startswith(QUERY_NAME_MARK):
            name = line[len(QUERY_NAME_MARK):].strip()
            lines = []
        elif name and line.strip() and not line.startswith("--"):
            lines.append(line)
            if line.rstrip().endswith(";"):
                queries[name] = "\n".join(lines)
                name = None
    return queries


def fetch_all(
    name: str,
    params: tuple = (),
    path: Path = DB_FILE,
) -> list[sqlite3.Row]:
    """Выполнить именованный запрос и вернуть все строки результата"""
    with closing(get_connection(path)) as conn:
        return conn.execute(load_queries()[name], params).fetchall()


def fetch_one(
    name: str,
    params: tuple = (),
    path: Path = DB_FILE,
) -> Optional[sqlite3.Row]:
    """Выполнить именованный запрос и вернуть первую строку результата"""
    with closing(get_connection(path)) as conn:
        return conn.execute(load_queries()[name], params).fetchone()
