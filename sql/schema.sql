CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'клиент'
);

CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    size TEXT NOT NULL CHECK (size IN ('малое', 'среднее', 'большое')),
    price_per_night INTEGER NOT NULL CHECK (price_per_night > 0)
);

CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    species TEXT NOT NULL,
    age_months INTEGER NOT NULL CHECK (age_months >= 0),
    weight_kg REAL NOT NULL CHECK (weight_kg > 0),
    is_vaccinated INTEGER NOT NULL CHECK (is_vaccinated IN (0, 1)),
    owner_id INTEGER NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    pet_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL,
    is_cancelled INTEGER NOT NULL DEFAULT 0 CHECK (is_cancelled IN (0, 1)),
    FOREIGN KEY (pet_id) REFERENCES pets(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    CHECK (check_out > check_in)
);
