import pytest

from pet_boarding.models import Pet, Room, User


@pytest.fixture
def owner():
    """Владелец питомцев"""
    return User(1, "Иванова Анна", "+7 900 111 22 33")


@pytest.fixture
def cat(owner):
    """Кошка, которая проходит условия приёма"""
    return Pet(1, "Барсик", "кошка", 18, 4.5, True, owner)


@pytest.fixture
def dog(owner):
    """Крупная собака, которой нужно большое место"""
    return Pet(2, "Рекс", "собака", 36, 24.0, True, owner)


@pytest.fixture
def small_room():
    """Малое место"""
    return Room(1, "Вольер 1", "малое", 800)


@pytest.fixture
def large_room():
    """Большое место"""
    return Room(5, "Апартаменты 1", "большое", 1800)
