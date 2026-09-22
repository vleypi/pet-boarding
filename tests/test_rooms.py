from datetime import date

from pet_boarding.constants import SIZE_SMALL
from pet_boarding.models import Room
from pet_boarding.models.rooms import (
    count_by_size,
    filter_rooms_for_pet,
    find_room_by_id,
    sort_rooms_by_price,
)


def test_room_creation(small_room):
    """Место хранит переданные данные"""
    assert small_room.id == 1
    assert small_room.name == "Вольер 1"
    assert small_room.size == SIZE_SMALL
    assert small_room.price_per_night == 800


def test_room_str(small_room):
    """Строковое представление места содержит название, размер и тариф"""
    assert str(small_room) == "Вольер 1, малое место, 800 рублей в сутки"


def test_room_is_suitable_for_pet(small_room, cat, dog):
    """Малое место подходит кошке и не подходит крупной собаке"""
    assert small_room.is_suitable_for(cat)
    assert not small_room.is_suitable_for(dog)


def test_room_cost_for_period(small_room):
    """Стоимость равна числу суток, умноженному на тариф места"""
    cost = small_room.cost_for(date(2026, 10, 1), date(2026, 10, 8))
    assert cost == 5600


def test_filter_rooms_for_pet(small_room, large_room, dog):
    """Для крупной собаки отбираются только большие места"""
    assert filter_rooms_for_pet([small_room, large_room], dog) == [large_room]


def test_sort_rooms_by_price(small_room, large_room):
    """Места сортируются по тарифу"""
    rooms = sort_rooms_by_price([large_room, small_room])
    assert rooms == [small_room, large_room]


def test_count_by_size(small_room, large_room):
    """Места считаются по каждому размеру, включая отсутствующие"""
    counters = count_by_size([small_room, large_room])
    assert counters == {"малое": 1, "среднее": 0, "большое": 1}


def test_room_restored_from_data(small_room):
    """Место восстанавливается из данных JSON без потерь"""
    restored = Room.from_data(small_room.to_data())
    assert restored.to_data() == small_room.to_data()


def test_find_unknown_room_returns_none(small_room):
    """Поиск несуществующего места возвращает None"""
    assert find_room_by_id([small_room], 99) is None
