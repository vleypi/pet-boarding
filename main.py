from datetime import date

PRICE_SMALL = 800
PRICE_MEDIUM = 1200
PRICE_LARGE = 1800

WEIGHT_SMALL = 5
WEIGHT_MEDIUM = 20

MIN_AGE_MONTHS = 3

owner_name = "Иванова Анна"
pet_name = "Барсик"
pet_species = "кошка"
pet_age_months = "18"
pet_weight_kg = "4.5"
pet_is_vaccinated = True
check_in_date = "2026-10-01"
check_out_date = "2026-10-08"


def can_accept_pet(species, age_months, is_vaccinated):
    is_allowed_species = species == "кошка" or species == "собака"
    is_old_enough = age_months >= MIN_AGE_MONTHS
    return is_allowed_species and is_old_enough and is_vaccinated


def choose_room_size(weight_kg):
    if weight_kg < WEIGHT_SMALL:
        return "малое"
    elif weight_kg < WEIGHT_MEDIUM:
        return "среднее"
    else:
        return "большое"


def calculate_boarding_cost(check_in, check_out, room_size):
    nights = (check_out - check_in).days
    if room_size == "малое":
        price_per_night = PRICE_SMALL
    elif room_size == "среднее":
        price_per_night = PRICE_MEDIUM
    else:
        price_per_night = PRICE_LARGE
    return nights * price_per_night


def main():
    age_months = int(pet_age_months)
    weight_kg = float(pet_weight_kg)
    check_in = date.fromisoformat(check_in_date)
    check_out = date.fromisoformat(check_out_date)

    print("Гостиница для животных, оформление бронирования")
    print(f"Клиент: {owner_name}")
    print(f"Питомец: {pet_name}, вид: {pet_species}")
    print(f"Возраст: {age_months} месяцев, вес: {weight_kg} кг")
    print(f"Даты: с {check_in} по {check_out}")

    if not can_accept_pet(pet_species, age_months, pet_is_vaccinated):
        print("Гостиница не может принять этого питомца")
        return

    nights = (check_out - check_in).days
    room_size = choose_room_size(weight_kg)
    cost = calculate_boarding_cost(check_in, check_out, room_size)

    print("Питомец принят")
    print(f"Подобрано место: {room_size}")
    print(f"Срок проживания: {nights} суток")
    print(f"Стоимость: {cost} рублей")


if __name__ == "__main__":
    main()
