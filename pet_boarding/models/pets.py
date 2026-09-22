from typing import Optional

from pet_boarding.constants import (
    ALLOWED_SPECIES,
    MEDIUM_ROOM_MAX_WEIGHT,
    MIN_AGE_MONTHS,
    SIZE_LARGE,
    SIZE_MEDIUM,
    SIZE_SMALL,
    SMALL_ROOM_MAX_WEIGHT,
)
from pet_boarding.models.common import next_id
from pet_boarding.models.users import User


class Pet:
    """Питомец, которого владелец оставляет в гостинице"""

    def __init__(
        self,
        pet_id: int,
        name: str,
        species: str,
        age_months: int,
        weight_kg: float,
        is_vaccinated: bool,
        owner: User,
    ) -> None:
        """Создать питомца"""
        self.id = pet_id
        self.name = name
        self.species = species
        self.age_months = age_months
        self.weight_kg = weight_kg
        self.is_vaccinated = is_vaccinated
        self.owner = owner

    def __str__(self) -> str:
        """Вернуть строковое представление питомца"""
        return (
            f"{self.name}, {self.species}, {self.weight_kg} кг, "
            f"владелец {self.owner.name}"
        )

    @staticmethod
    def is_supported_species(species: str) -> bool:
        """Проверить, принимает ли гостиница животных этого вида"""
        return species in ALLOWED_SPECIES

    def rejection_reason(self) -> str:
        """Вернуть причину отказа или пустую строку, если отказа нет"""
        if not Pet.is_supported_species(self.species):
            return "гостиница принимает только кошек и собак"
        if self.age_months < MIN_AGE_MONTHS:
            return f"возраст меньше {MIN_AGE_MONTHS} месяцев"
        if not self.is_vaccinated:
            return "у питомца нет прививок"
        return ""

    def can_be_accepted(self) -> bool:
        """Проверить, может ли гостиница принять питомца"""
        return not self.rejection_reason()

    def required_room_size(self) -> str:
        """Подобрать размер места по весу питомца"""
        if self.weight_kg < SMALL_ROOM_MAX_WEIGHT:
            return SIZE_SMALL
        if self.weight_kg < MEDIUM_ROOM_MAX_WEIGHT:
            return SIZE_MEDIUM
        return SIZE_LARGE

    @classmethod
    def from_data(cls, data: dict, owner: User) -> "Pet":
        """Создать питомца из данных JSON и объекта владельца"""
        return cls(
            pet_id=data["id"],
            name=data["name"],
            species=data["species"],
            age_months=data["age_months"],
            weight_kg=data["weight_kg"],
            is_vaccinated=data["is_vaccinated"],
            owner=owner,
        )

    def to_data(self) -> dict:
        """Вернуть данные питомца для записи в JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "age_months": self.age_months,
            "weight_kg": self.weight_kg,
            "is_vaccinated": self.is_vaccinated,
            "owner_id": self.owner.id,
        }


def find_pet_by_id(pets: list[Pet], pet_id: int) -> Optional[Pet]:
    """Найти питомца по идентификатору"""
    return next((pet for pet in pets if pet.id == pet_id), None)


def add_pet(
    pets: list[Pet],
    name: str,
    species: str,
    age_months: int,
    weight_kg: float,
    is_vaccinated: bool,
    owner: User,
) -> Pet:
    """Создать питомца и добавить его в список"""
    pet = Pet(
        next_id(pets),
        name,
        species,
        age_months,
        weight_kg,
        is_vaccinated,
        owner,
    )
    pets.append(pet)
    return pet


def find_pets(pets: list[Pet], query: str) -> list[Pet]:
    """Найти питомцев по части клички или имени владельца"""
    query = query.lower()
    return [
        pet
        for pet in pets
        if query in pet.name.lower() or query in pet.owner.name.lower()
    ]


def sort_pets_by_weight(pets: list[Pet]) -> list[Pet]:
    """Вернуть питомцев, упорядоченных по весу"""
    return sorted(pets, key=lambda pet: pet.weight_kg)


def count_by_species(pets: list[Pet]) -> dict[str, int]:
    """Посчитать количество питомцев каждого вида"""
    counters: dict[str, int] = {}
    for pet in pets:
        counters[pet.species] = counters.get(pet.species, 0) + 1
    return counters
