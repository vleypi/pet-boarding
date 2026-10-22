-- name: room_list
-- Список всех мест по возрастанию тарифа
SELECT id, name, size, price_per_night
FROM rooms
ORDER BY price_per_night, name;

-- name: pet_list
-- Список питомцев с именами владельцев по весу
SELECT pets.id, pets.name, pets.species, pets.weight_kg,
       users.name AS owner_name
FROM pets
JOIN users ON pets.owner_id = users.id
ORDER BY pets.weight_kg;

-- name: rooms_by_size
-- Места выбранного размера, размер передаётся параметром
SELECT id, name, size, price_per_night
FROM rooms
WHERE size = ?
ORDER BY price_per_night, name;

-- name: acceptable_pets
-- Питомцы, которых гостиница может принять: кошки и собаки от 3 месяцев с прививками
SELECT pets.id, pets.name, pets.species, pets.weight_kg,
       users.name AS owner_name
FROM pets
JOIN users ON pets.owner_id = users.id
WHERE pets.species IN ('кошка', 'собака')
  AND pets.age_months >= 3
  AND pets.is_vaccinated = 1
ORDER BY pets.weight_kg;

-- name: booking_list
-- Все бронирования с питомцем, владельцем, местом, сроком, стоимостью и статусом
SELECT bookings.id,
       pets.id AS pet_id, pets.name AS pet_name,
       users.name AS owner_name,
       rooms.id AS room_id, rooms.name AS room_name,
       strftime('%d.%m.%Y', bookings.check_in) AS check_in,
       strftime('%d.%m.%Y', bookings.check_out) AS check_out,
       CAST(julianday(bookings.check_out) - julianday(bookings.check_in) AS INTEGER) AS nights,
       CAST((julianday(bookings.check_out) - julianday(bookings.check_in)) * rooms.price_per_night AS INTEGER) AS cost,
       bookings.is_cancelled,
       CASE WHEN bookings.is_cancelled = 1 THEN 'отменено' ELSE 'активно' END AS status
FROM bookings
JOIN pets ON bookings.pet_id = pets.id
JOIN users ON pets.owner_id = users.id
JOIN rooms ON bookings.room_id = rooms.id
ORDER BY bookings.check_in;

-- name: active_booking_list
-- Только активные бронирования с теми же сведениями
SELECT bookings.id,
       pets.id AS pet_id, pets.name AS pet_name,
       users.name AS owner_name,
       rooms.id AS room_id, rooms.name AS room_name,
       strftime('%d.%m.%Y', bookings.check_in) AS check_in,
       strftime('%d.%m.%Y', bookings.check_out) AS check_out,
       CAST(julianday(bookings.check_out) - julianday(bookings.check_in) AS INTEGER) AS nights,
       CAST((julianday(bookings.check_out) - julianday(bookings.check_in)) * rooms.price_per_night AS INTEGER) AS cost,
       bookings.is_cancelled,
       'активно' AS status
FROM bookings
JOIN pets ON bookings.pet_id = pets.id
JOIN users ON pets.owner_id = users.id
JOIN rooms ON bookings.room_id = rooms.id
WHERE bookings.is_cancelled = 0
ORDER BY bookings.check_in;

-- name: available_rooms
-- Места, свободные на период: нет активной брони, которая пересекается с датами
-- Параметры: дата выезда, дата заезда, размер места (пустая строка значит любой)
SELECT id, name, size, price_per_night
FROM rooms
WHERE id NOT IN (
    SELECT room_id
    FROM bookings
    WHERE is_cancelled = 0
      AND check_in < ?
      AND ? < check_out
)
  AND (? = '' OR size = ?)
ORDER BY price_per_night, name;

-- name: active_bookings_count
-- Количество активных бронирований
SELECT COUNT(*) AS bookings_count
FROM bookings
WHERE is_cancelled = 0;

-- name: income_summary
-- Выручка, число суток и средний срок по активным бронированиям
SELECT COUNT(bookings.id) AS bookings_count,
       CAST(COALESCE(SUM((julianday(check_out) - julianday(check_in)) * rooms.price_per_night), 0) AS INTEGER) AS income,
       CAST(COALESCE(SUM(julianday(check_out) - julianday(check_in)), 0) AS INTEGER) AS nights,
       ROUND(COALESCE(AVG(julianday(check_out) - julianday(check_in)), 0), 1) AS average_nights,
       MIN(check_in) AS first_check_in,
       MAX(check_out) AS last_check_out
FROM bookings
JOIN rooms ON bookings.room_id = rooms.id
WHERE bookings.is_cancelled = 0;

-- name: bookings_per_room
-- Число активных бронирований и суток по каждому месту, места без броней тоже попадают
SELECT rooms.id, rooms.name, rooms.size,
       COUNT(bookings.id) AS bookings_count,
       CAST(COALESCE(SUM(julianday(bookings.check_out) - julianday(bookings.check_in)), 0) AS INTEGER) AS nights
FROM rooms
LEFT JOIN bookings
    ON rooms.id = bookings.room_id
   AND bookings.is_cancelled = 0
GROUP BY rooms.id, rooms.name, rooms.size
ORDER BY bookings_count DESC, rooms.name;

-- name: pets_by_species
-- Количество питомцев и средний вес по видам
SELECT species,
       COUNT(*) AS pets_count,
       ROUND(AVG(weight_kg), 1) AS average_weight
FROM pets
GROUP BY species
ORDER BY pets_count DESC;

-- name: income_by_size
-- Выручка и число броней по размерам мест
SELECT rooms.size,
       COUNT(bookings.id) AS bookings_count,
       CAST(COALESCE(SUM((julianday(bookings.check_out) - julianday(bookings.check_in)) * rooms.price_per_night), 0) AS INTEGER) AS income
FROM rooms
LEFT JOIN bookings
    ON rooms.id = bookings.room_id
   AND bookings.is_cancelled = 0
GROUP BY rooms.size
ORDER BY income DESC;

-- name: popular_rooms
-- Места, у которых активных бронирований не меньше заданного числа
SELECT rooms.id, rooms.name,
       COUNT(bookings.id) AS bookings_count
FROM rooms
JOIN bookings ON rooms.id = bookings.room_id
WHERE bookings.is_cancelled = 0
GROUP BY rooms.id, rooms.name
HAVING COUNT(bookings.id) >= ?
ORDER BY bookings_count DESC, rooms.name;

-- name: owners_with_several_pets
-- Владельцы, у которых больше одного питомца
SELECT users.id, users.name, users.phone,
       COUNT(pets.id) AS pets_count
FROM users
JOIN pets ON pets.owner_id = users.id
GROUP BY users.id, users.name, users.phone
HAVING COUNT(pets.id) > 1
ORDER BY pets_count DESC, users.name;

-- name: upcoming_check_ins
-- Ближайшие активные заезды начиная с заданной даты, не больше заданного числа
SELECT bookings.id, pets.name AS pet_name, rooms.name AS room_name,
       strftime('%d.%m.%Y', bookings.check_in) AS check_in
FROM bookings
JOIN pets ON bookings.pet_id = pets.id
JOIN rooms ON bookings.room_id = rooms.id
WHERE bookings.is_cancelled = 0
  AND bookings.check_in >= ?
ORDER BY bookings.check_in
LIMIT ?;
