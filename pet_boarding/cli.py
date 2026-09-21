"""Меню приложения и вывод данных"""

from pet_boarding import bookings, pets, rooms, storage
from pet_boarding.utils import (
    input_date,
    input_float,
    input_int,
    input_text,
    input_yes_no,
)

MENU = """
Гостиница для домашних животных

1. Показать места
2. Показать питомцев
3. Добавить питомца
4. Найти питомца
5. Оформить бронирование
6. Отменить бронирование
7. Показать бронирования
8. Статистика
0. Выход
"""


def show_rooms(rooms_data: dict[int, dict]) -> None:
    """Вывести список мест"""
    if not rooms_data:
        print("Мест нет")
        return
    print(f"\n{'Номер':<7}{'Название':<18}{'Размер':<10}{'Тариф':>7}")
    for room in rooms.sort_rooms_by_price(rooms_data):
        print(
            f"{room['id']:<7}{room['name']:<18}"
            f"{room['size']:<10}{room['price_per_night']:>7}"
        )


def show_pets(pets_data: dict[int, dict]) -> None:
    """Вывести список питомцев"""
    if not pets_data:
        print("Питомцев нет")
        return
    print(f"\n{'Номер':<7}{'Кличка':<12}{'Вид':<10}{'Вес':>6}  Владелец")
    for pet in pets.sort_pets_by_weight(pets_data):
        print(
            f"{pet['id']:<7}{pet['name']:<12}"
            f"{pet['species']:<10}{pet['weight_kg']:>6}  {pet['owner']}"
        )


def show_bookings(
    bookings_data: list[dict],
    pets_data: dict[int, dict],
    rooms_data: dict[int, dict],
) -> None:
    """Вывести список бронирований"""
    if not bookings_data:
        print("Бронирований нет")
        return
    print(f"\n{'Номер':<7}{'Питомец':<12}{'Место':<18}{'Заезд':<12}Выезд")
    for booking in bookings.sort_bookings_by_date(bookings_data):
        pet = pets_data.get(booking["pet_id"], {})
        room = rooms_data.get(booking["room_id"], {})
        print(
            f"{booking['id']:<7}{pet.get('name', 'неизвестен'):<12}"
            f"{room.get('name', 'неизвестно'):<18}"
            f"{booking['check_in']:<12}{booking['check_out']}"
        )


def show_statistics(
    bookings_data: list[dict],
    pets_data: dict[int, dict],
    rooms_data: dict[int, dict],
) -> None:
    """Вывести статистику приложения"""
    stats = bookings.get_statistics(bookings_data, rooms_data)
    print(f"\nВсего бронирований: {stats['bookings']}")
    print(f"Забронировано суток: {stats['nights']}")
    print(f"Средний срок: {stats['average_nights']} суток")
    print(f"Выручка: {stats['income']} рублей")
    print(f"Питомцев по видам: {pets.count_by_species(pets_data)}")
    print(f"Мест по размерам: {rooms.count_by_size(rooms_data)}")


def add_pet_dialog(pets_data: dict[int, dict]) -> None:
    """Добавить питомца по данным от пользователя"""
    name = input_text("Кличка: ")
    species = input_text("Вид (кошка или собака): ").lower()
    age_months = input_int("Возраст в месяцах: ", 0)
    weight_kg = input_float("Вес в килограммах: ", 0.1)
    is_vaccinated = input_yes_no("Есть прививки (да или нет): ")
    owner = input_text("Владелец: ")
    pet_id = pets.add_pet(
        pets_data,
        name,
        species,
        age_months,
        weight_kg,
        is_vaccinated,
        owner,
    )
    storage.save_pets(pets_data)
    print(f"Питомец добавлен под номером {pet_id}")


def find_pet_dialog(pets_data: dict[int, dict]) -> None:
    """Найти питомцев по кличке или владельцу"""
    query = input_text("Часть клички или фамилии владельца: ")
    found = pets.find_pets(pets_data, query)
    if not found:
        print("Ничего не найдено")
        return
    for pet in found:
        print(f"{pet['id']}. {pet['name']}, {pet['species']}, {pet['owner']}")


def create_booking_dialog(
    bookings_data: list[dict],
    pets_data: dict[int, dict],
    rooms_data: dict[int, dict],
) -> None:
    """Оформить бронирование"""
    show_pets(pets_data)
    try:
        pet = pets.get_pet(pets_data, input_int("\nНомер питомца: ", 1))
    except KeyError as error:
        print(f"Ошибка: {error}")
        return

    reason = pets.rejection_reason(
        pet["species"],
        pet["age_months"],
        pet["is_vaccinated"],
    )
    if reason:
        print(f"Питомца принять нельзя: {reason}")
        return

    size = pets.choose_room_size(pet["weight_kg"])
    print(f"Питомцу {pet['name']} подходит {size} место")

    check_in = input_date("Дата заезда (ГГГГ-ММ-ДД): ")
    check_out = input_date("Дата выезда (ГГГГ-ММ-ДД): ")
    if check_out <= check_in:
        print("Дата выезда должна быть позже даты заезда")
        return

    free = [
        room
        for room in rooms.filter_rooms_by_size(rooms_data, size)
        if bookings.is_room_available(
            bookings_data,
            room["id"],
            check_in,
            check_out,
        )
    ]
    if not free:
        print(bookings.get_booking_status(False))
        return

    print("\nСвободные места:")
    for room in free:
        cost = bookings.calculate_boarding_cost(
            check_in,
            check_out,
            room["price_per_night"],
        )
        print(f"{room['id']}. {room['name']}, стоимость {cost} рублей")

    room_id = input_int("\nНомер места: ", 1)
    try:
        booking = bookings.create_booking(
            bookings_data,
            pet["id"],
            room_id,
            check_in,
            check_out,
        )
    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    storage.save_bookings(bookings_data)
    price = rooms.get_room_price(rooms_data, room_id)
    cost = bookings.calculate_boarding_cost(check_in, check_out, price)
    nights = bookings.count_nights(check_in, check_out)
    print(f"Бронирование {booking['id']} создано")
    print(f"Срок {nights} суток, к оплате {cost} рублей")


def cancel_booking_dialog(
    bookings_data: list[dict],
    pets_data: dict[int, dict],
    rooms_data: dict[int, dict],
) -> None:
    """Отменить бронирование"""
    show_bookings(bookings_data, pets_data, rooms_data)
    if not bookings_data:
        return
    booking_id = input_int("\nНомер бронирования: ", 1)
    if bookings.cancel_booking(bookings_data, booking_id):
        storage.save_bookings(bookings_data)
        print("Бронирование отменено")
    else:
        print("Бронирование с таким номером не найдено")


def run() -> None:
    """Запустить приложение"""
    rooms_data = storage.load_rooms()
    pets_data = storage.load_pets()
    bookings_data = storage.load_bookings()

    while True:
        print(MENU)
        choice = input_int("Выберите действие: ", 0)
        if choice == 0:
            print("Работа завершена")
            break
        elif choice == 1:
            show_rooms(rooms_data)
        elif choice == 2:
            show_pets(pets_data)
        elif choice == 3:
            add_pet_dialog(pets_data)
        elif choice == 4:
            find_pet_dialog(pets_data)
        elif choice == 5:
            create_booking_dialog(bookings_data, pets_data, rooms_data)
        elif choice == 6:
            cancel_booking_dialog(bookings_data, pets_data, rooms_data)
        elif choice == 7:
            show_bookings(bookings_data, pets_data, rooms_data)
        elif choice == 8:
            show_statistics(bookings_data, pets_data, rooms_data)
        else:
            print("Такого пункта нет")
