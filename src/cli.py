from src import storage
from src.exceptions import BookingError
from src.models import Booking, Pet, Room, User
from src.models.bookings import (
    cancel_booking,
    create_booking,
    get_booking_status,
    get_statistics,
    is_room_available,
    sort_bookings_by_date,
    validate_period,
)
from src.models.pets import (
    add_pet,
    count_by_species,
    find_pet_by_id,
    find_pets,
    sort_pets_by_weight,
)
from src.models.rooms import (
    count_by_size,
    filter_rooms_for_pet,
    find_room_by_id,
    sort_rooms_by_price,
)
from src.models.users import add_user, find_user_by_id
from src.utils import (
    input_date,
    input_float,
    input_int,
    input_text,
    input_yes_no,
)

MENU = """
Гостиница для домашних животных

1. Показать места
2. Показать владельцев
3. Добавить владельца
4. Показать питомцев
5. Добавить питомца
6. Найти питомца
7. Оформить бронирование
8. Отменить бронирование
9. Показать бронирования
10. Статистика
0. Выход
"""


def show_rooms(rooms: list[Room]) -> None:
    """Вывести список мест"""
    if not rooms:
        print("Мест нет")
        return
    print(f"\n{'Номер':<7}{'Название':<18}{'Размер':<10}{'Тариф':>7}")
    for room in sort_rooms_by_price(rooms):
        print(
            f"{room.id:<7}{room.name:<18}"
            f"{room.size:<10}{room.price_per_night:>7}"
        )


def show_users(users: list[User]) -> None:
    """Вывести список пользователей"""
    if not users:
        print("Пользователей нет")
        return
    print()
    for user in users:
        print(f"{user.id}. {user}")


def add_user_dialog(users: list[User]) -> None:
    """Добавить владельца по данным от пользователя"""
    name = input_text("Имя и фамилия: ")
    phone = input_text("Телефон: ")
    user = add_user(users, name, phone)
    storage.save_users(users)
    print(f"Владелец добавлен под номером {user.id}: {user}")


def show_pets(pets: list[Pet]) -> None:
    """Вывести список питомцев"""
    if not pets:
        print("Питомцев нет")
        return
    print(f"\n{'Номер':<7}{'Кличка':<12}{'Вид':<10}{'Вес':>6}  Владелец")
    for pet in sort_pets_by_weight(pets):
        print(
            f"{pet.id:<7}{pet.name:<12}"
            f"{pet.species:<10}{pet.weight_kg:>6}  {pet.owner.name}"
        )


def input_species() -> str:
    """Запросить вид питомца, который принимает гостиница"""
    while True:
        species = input_text("Вид (кошка или собака): ").lower()
        if Pet.is_supported_species(species):
            return species
        print("Гостиница принимает только кошек и собак")


def add_pet_dialog(pets: list[Pet], users: list[User]) -> None:
    """Добавить питомца по данным от пользователя"""
    show_users(users)
    owner = find_user_by_id(users, input_int("\nНомер владельца: ", 1))
    if owner is None:
        print("Владелец не найден, сначала добавьте его в пункте 3")
        return
    pet = add_pet(
        pets,
        input_text("Кличка: "),
        input_species(),
        input_int("Возраст в месяцах: ", 0),
        input_float("Вес в килограммах: ", 0.1),
        input_yes_no("Есть прививки (да или нет): "),
        owner,
    )
    storage.save_pets(pets)
    print(f"Питомец добавлен под номером {pet.id}: {pet}")


def find_pet_dialog(pets: list[Pet]) -> None:
    """Найти питомцев по кличке или имени владельца"""
    query = input_text("Часть клички или имени владельца: ")
    found = find_pets(pets, query)
    if not found:
        print("Ничего не найдено")
        return
    for pet in found:
        print(f"{pet.id}. {pet}")


def show_bookings(bookings: list[Booking]) -> None:
    """Вывести список бронирований"""
    if not bookings:
        print("Бронирований нет")
        return
    print(
        f"\n{'Номер':<7}{'Питомец':<10}{'Место':<15}"
        f"{'Заезд':<12}{'Выезд':<12}Статус"
    )
    for booking in sort_bookings_by_date(bookings):
        print(
            f"{booking.id:<7}{booking.pet.name:<10}{booking.room.name:<15}"
            f"{booking.check_in!s:<12}{booking.check_out!s:<12}"
            f"{booking.status}"
        )


def create_booking_dialog(
    bookings: list[Booking],
    pets: list[Pet],
    rooms: list[Room],
) -> None:
    """Оформить бронирование"""
    show_pets(pets)
    pet = find_pet_by_id(pets, input_int("\nНомер питомца: ", 1))
    if pet is None:
        print("Питомец не найден")
        return
    reason = pet.rejection_reason()
    if reason:
        print(f"Питомца принять нельзя: {reason}")
        return
    print(f"Питомцу {pet.name} нужно {pet.required_room_size()} место")

    check_in = input_date("Дата заезда (ГГГГ-ММ-ДД): ")
    check_out = input_date("Дата выезда (ГГГГ-ММ-ДД): ")
    try:
        validate_period(check_in, check_out)
    except BookingError as error:
        print(f"Ошибка: {error}")
        return

    free = [
        room
        for room in filter_rooms_for_pet(rooms, pet)
        if is_room_available(bookings, room, check_in, check_out)
    ]
    if not free:
        print(get_booking_status(False))
        return
    print("\nСвободные места:")
    for room in free:
        cost = room.cost_for(check_in, check_out)
        print(f"{room.id}. {room}, за период {cost} рублей")

    room = find_room_by_id(rooms, input_int("\nНомер места: ", 1))
    if room is None:
        print("Место не найдено")
        return
    try:
        booking = create_booking(bookings, pet, room, check_in, check_out)
    except BookingError as error:
        print(f"Бронирование не создано: {error}")
        return
    storage.save_bookings(bookings)
    print(booking)
    print(f"Срок {booking.nights} суток, к оплате {booking.cost} рублей")


def cancel_booking_dialog(bookings: list[Booking]) -> None:
    """Отменить бронирование"""
    show_bookings(bookings)
    if not bookings:
        return
    booking_id = input_int("\nНомер бронирования: ", 1)
    if cancel_booking(bookings, booking_id):
        storage.save_bookings(bookings)
        print("Бронирование отменено")
    else:
        print("Активное бронирование с таким номером не найдено")


def show_statistics(
    bookings: list[Booking],
    pets: list[Pet],
    rooms: list[Room],
) -> None:
    """Вывести статистику приложения"""
    stats = get_statistics(bookings)
    print(f"\nАктивных бронирований: {stats['active']}")
    print(f"Отменённых бронирований: {stats['cancelled']}")
    print(f"Забронировано суток: {stats['nights']}")
    print(f"Средний срок: {stats['average_nights']} суток")
    print(f"Выручка: {stats['income']} рублей")
    print(f"Питомцев по видам: {count_by_species(pets)}")
    print(f"Мест по размерам: {count_by_size(rooms)}")


def run() -> None:
    """Загрузить данные и запустить меню приложения"""
    users = storage.load_users()
    rooms = storage.load_rooms()
    pets = storage.load_pets(users)
    bookings = storage.load_bookings(pets, rooms)

    while True:
        print(MENU)
        choice = input_int("Выберите действие: ", 0)
        if choice == 0:
            print("Работа завершена")
            break
        elif choice == 1:
            show_rooms(rooms)
        elif choice == 2:
            show_users(users)
        elif choice == 3:
            add_user_dialog(users)
        elif choice == 4:
            show_pets(pets)
        elif choice == 5:
            add_pet_dialog(pets, users)
        elif choice == 6:
            find_pet_dialog(pets)
        elif choice == 7:
            create_booking_dialog(bookings, pets, rooms)
        elif choice == 8:
            cancel_booking_dialog(bookings)
        elif choice == 9:
            show_bookings(bookings)
        elif choice == 10:
            show_statistics(bookings, pets, rooms)
        else:
            print("Такого пункта нет")
