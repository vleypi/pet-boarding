from typing import Optional

from pet_boarding.constants import ROLE_ADMIN, ROLE_CLIENT
from pet_boarding.models.common import next_id


class User:
    """Пользователь системы: владелец питомца или администратор"""

    def __init__(
        self,
        user_id: int,
        name: str,
        phone: str,
        role: str = ROLE_CLIENT,
    ) -> None:
        """Создать пользователя"""
        self.id = user_id
        self.name = name
        self.phone = phone
        self.role = role

    def __str__(self) -> str:
        """Вернуть строковое представление пользователя"""
        if self.role == ROLE_ADMIN:
            return f"{self.name}, {self.phone}, {self.role}"
        return f"{self.name}, {self.phone}"

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из данных JSON"""
        return cls(
            user_id=data["id"],
            name=data["name"],
            phone=data["phone"],
            role=data.get("role", ROLE_CLIENT),
        )

    def to_data(self) -> dict:
        """Вернуть данные пользователя для записи в JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "role": self.role,
        }


def find_user_by_id(users: list[User], user_id: int) -> Optional[User]:
    """Найти пользователя по идентификатору"""
    return next((user for user in users if user.id == user_id), None)


def add_user(users: list[User], name: str, phone: str) -> User:
    """Создать владельца и добавить его в список"""
    user = User(next_id(users), name, phone)
    users.append(user)
    return user
