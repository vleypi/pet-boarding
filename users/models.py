from django.db import models

from src.constants import ROLE_ADMIN, ROLE_CLIENT


class User(models.Model):
    """Пользователь системы: владелец питомца или администратор"""

    ROLE_CHOICES = [(ROLE_CLIENT, ROLE_CLIENT), (ROLE_ADMIN, ROLE_ADMIN)]

    name = models.CharField(max_length=150, verbose_name="Имя")
    phone = models.CharField(
        max_length=30,
        verbose_name="Телефон",
        help_text="Например, +7 900 111 22 33",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CLIENT,
        verbose_name="Роль",
    )

    class Meta:
        """Порядок, названия и ограничения таблицы пользователей"""

        ordering = ["name"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=[ROLE_CLIENT, ROLE_ADMIN]),
                name="user_role_valid",
            ),
        ]

    def __str__(self) -> str:
        """Вернуть имя пользователя"""
        return self.name

    @property
    def is_admin(self) -> bool:
        """Проверить, является ли пользователь администратором"""
        return self.role == ROLE_ADMIN
