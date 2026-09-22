from pet_boarding.constants import (
    ALLOWED_SPECIES,
    MEDIUM_ROOM_MAX_WEIGHT,
    MIN_AGE_MONTHS,
    SIZE_LARGE,
    SIZE_MEDIUM,
    SIZE_SMALL,
    SMALL_ROOM_MAX_WEIGHT,
)


def can_accept_pet(
    species: str,
    age_months: int,
    is_vaccinated: bool,
) -> bool:
    """Проверить, может ли гостиница принять питомца"""
    is_allowed_species = species in ALLOWED_SPECIES
    is_old_enough = age_months >= MIN_AGE_MONTHS
    return is_allowed_species and is_old_enough and is_vaccinated


def rejection_reason(
    species: str,
    age_months: int,
    is_vaccinated: bool,
) -> str:
    """Вернуть причину отказа или пустую строку, если отказа нет"""
    if species not in ALLOWED_SPECIES:
        return "гостиница принимает только кошек и собак"
    if age_months < MIN_AGE_MONTHS:
        return f"возраст меньше {MIN_AGE_MONTHS} месяцев"
    if not is_vaccinated:
        return "у питомца нет прививок"
    return ""


def choose_room_size(weight_kg: float) -> str:
    """Подобрать размер места по весу питомца"""
    if weight_kg < SMALL_ROOM_MAX_WEIGHT:
        return SIZE_SMALL
    elif weight_kg < MEDIUM_ROOM_MAX_WEIGHT:
        return SIZE_MEDIUM
    else:
        return SIZE_LARGE


def next_pet_id(pets: dict[int, dict]) -> int:
    """Вернуть свободный идентификатор питомца"""
    if not pets:
        return 1
    return max(pets) + 1


def add_pet(
    pets: dict[int, dict],
    name: str,
    species: str,
    age_months: int,
    weight_kg: float,
    is_vaccinated: bool,
    owner: str,
) -> int:
    """Добавить питомца и вернуть его идентификатор"""
    pet_id = next_pet_id(pets)
    pets[pet_id] = {
        "id": pet_id,
        "name": name,
        "species": species,
        "age_months": age_months,
        "weight_kg": weight_kg,
        "is_vaccinated": is_vaccinated,
        "owner": owner,
    }
    return pet_id


def get_pet(pets: dict[int, dict], pet_id: int) -> dict:
    """Вернуть питомца по идентификатору"""
    if pet_id not in pets:
        raise KeyError(f"питомец с номером {pet_id} не найден")
    return pets[pet_id]


def find_pets(pets: dict[int, dict], query: str) -> list[dict]:
    """Найти питомцев по части клички или фамилии владельца"""
    query = query.lower()
    found = []
    for pet in pets.values():
        if query in pet["name"].lower() or query in pet["owner"].lower():
            found.append(pet)
    return found


def sort_pets_by_weight(pets: dict[int, dict]) -> list[dict]:
    """Вернуть питомцев, упорядоченных по весу"""
    return sorted(pets.values(), key=lambda pet: pet["weight_kg"])


def count_by_species(pets: dict[int, dict]) -> dict[str, int]:
    """Посчитать количество питомцев каждого вида"""
    counters: dict[str, int] = {}
    for pet in pets.values():
        counters[pet["species"]] = counters.get(pet["species"], 0) + 1
    return counters
