"""Константы проекта"""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ROOMS_FILE = DATA_DIR / "rooms.json"
PETS_FILE = DATA_DIR / "pets.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"

ENCODING = "utf-8"
JSON_INDENT = 4

SIZE_SMALL = "малое"
SIZE_MEDIUM = "среднее"
SIZE_LARGE = "большое"

ROOM_SIZES = (SIZE_SMALL, SIZE_MEDIUM, SIZE_LARGE)

ALLOWED_SPECIES = {"кошка", "собака"}

MIN_AGE_MONTHS = 3

SMALL_ROOM_MAX_WEIGHT = 5
MEDIUM_ROOM_MAX_WEIGHT = 20

ROLE_CLIENT = "клиент"
ROLE_ADMIN = "администратор"
