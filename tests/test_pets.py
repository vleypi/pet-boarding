"""Тесты функций работы с питомцами"""

from pet_boarding.pets import (
    add_pet,
    can_accept_pet,
    choose_room_size,
    find_pets,
)


def test_can_accept_healthy_pet():
    """Кошка с прививками старше трёх месяцев принимается"""
    assert can_accept_pet("кошка", 18, True)


def test_reject_pet_without_vaccination():
    """Питомец без прививок не принимается"""
    assert not can_accept_pet("собака", 36, False)


def test_reject_too_young_pet():
    """Питомец младше трёх месяцев не принимается"""
    assert not can_accept_pet("кошка", 2, True)


def test_reject_unsupported_species():
    """Гостиница принимает только кошек и собак"""
    assert not can_accept_pet("попугай", 24, True)


def test_choose_room_size_by_weight():
    """Размер места подбирается по весу питомца"""
    assert choose_room_size(4.5) == "малое"
    assert choose_room_size(12.5) == "среднее"
    assert choose_room_size(24.0) == "большое"


def test_add_pet_returns_new_id():
    """Добавленный питомец получает номер и попадает в словарь"""
    pets = {}
    pet_id = add_pet(pets, "Барсик", "кошка", 18, 4.5, True, "Иванова")
    assert pet_id == 1
    assert pets[pet_id]["name"] == "Барсик"


def test_find_pets_by_name_part():
    """Поиск находит питомца по части клички"""
    pets = {}
    add_pet(pets, "Барсик", "кошка", 18, 4.5, True, "Иванова")
    assert find_pets(pets, "бар")
