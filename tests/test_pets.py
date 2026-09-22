from pet_boarding.constants import SIZE_LARGE, SIZE_MEDIUM, SIZE_SMALL
from pet_boarding.models import Pet
from pet_boarding.models.pets import (
    add_pet,
    count_by_species,
    find_pets,
    sort_pets_by_weight,
)


def test_healthy_pet_is_accepted(cat):
    """Кошка с прививками старше трёх месяцев принимается"""
    assert cat.can_be_accepted()
    assert cat.rejection_reason() == ""


def test_pet_without_vaccination_is_rejected(owner):
    """Питомец без прививок не принимается"""
    pet = Pet(3, "Мухтар", "собака", 8, 12.5, False, owner)
    assert not pet.can_be_accepted()
    assert "прививок" in pet.rejection_reason()


def test_too_young_pet_is_rejected(owner):
    """Питомец младше трёх месяцев не принимается"""
    pet = Pet(4, "Пушок", "кошка", 2, 1.2, True, owner)
    assert not pet.can_be_accepted()


def test_unsupported_species_is_rejected(owner):
    """Гостиница принимает только кошек и собак"""
    pet = Pet(5, "Кеша", "попугай", 24, 0.3, True, owner)
    assert not pet.can_be_accepted()


def test_is_supported_species_called_on_class():
    """Проверка вида вызывается через класс без создания объекта"""
    assert Pet.is_supported_species("собака")
    assert not Pet.is_supported_species("хомяк")


def test_required_room_size_by_weight(owner):
    """Размер места подбирается по весу питомца"""
    sizes = [
        Pet(1, "Тест", "кошка", 12, weight, True, owner).required_room_size()
        for weight in (4.5, 12.5, 24.0)
    ]
    assert sizes == [SIZE_SMALL, SIZE_MEDIUM, SIZE_LARGE]


def test_pet_keeps_owner_object(cat, owner):
    """Питомец хранит сам объект владельца, а в JSON пишет его номер"""
    assert cat.owner is owner
    assert cat.to_data()["owner_id"] == owner.id


def test_pet_restored_from_data(cat, owner):
    """Питомец восстанавливается из данных JSON и объекта владельца"""
    restored = Pet.from_data(cat.to_data(), owner)
    assert restored.to_data() == cat.to_data()
    assert restored.owner is owner


def test_add_pet_assigns_next_id(owner):
    """Добавленный питомец получает номер и попадает в список"""
    pets = []
    pet = add_pet(pets, "Барсик", "кошка", 18, 4.5, True, owner)
    assert pet.id == 1
    assert pets == [pet]


def test_find_pets_by_name_or_owner(cat, dog):
    """Поиск находит питомцев по части клички и по имени владельца"""
    assert find_pets([cat, dog], "бар") == [cat]
    assert find_pets([cat, dog], "иванова") == [cat, dog]


def test_sort_and_count_pets(cat, dog):
    """Питомцы сортируются по весу и считаются по видам"""
    assert sort_pets_by_weight([dog, cat]) == [cat, dog]
    assert count_by_species([cat, dog]) == {"кошка": 1, "собака": 1}
