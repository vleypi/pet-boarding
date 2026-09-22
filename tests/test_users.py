from pet_boarding.constants import ROLE_ADMIN, ROLE_CLIENT
from pet_boarding.models import User
from pet_boarding.models.users import add_user, find_user_by_id


def test_user_creation():
    """Пользователь хранит переданные данные, роль по умолчанию клиент"""
    user = User(1, "Иванова Анна", "+7 900 111 22 33")
    assert user.id == 1
    assert user.name == "Иванова Анна"
    assert user.phone == "+7 900 111 22 33"
    assert user.role == ROLE_CLIENT


def test_user_str_shows_role_only_for_admin(owner):
    """Роль видна в строковом представлении только у администратора"""
    admin = User(2, "Кузнецова Мария", "+7 900 000 11 22", ROLE_ADMIN)
    assert ROLE_ADMIN in str(admin)
    assert ROLE_CLIENT not in str(owner)


def test_user_restored_from_data(owner):
    """Пользователь восстанавливается из данных JSON без потерь"""
    restored = User.from_data(owner.to_data())
    assert isinstance(restored, User)
    assert restored.to_data() == owner.to_data()


def test_add_user_assigns_next_id(owner):
    """Новый пользователь получает следующий номер и попадает в список"""
    users = [owner]
    user = add_user(users, "Петров Сергей", "+7 900 444 55 66")
    assert user.id == 2
    assert users == [owner, user]


def test_find_unknown_user_returns_none(owner):
    """Поиск несуществующего пользователя возвращает None"""
    assert find_user_by_id([owner], 99) is None
