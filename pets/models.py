from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from src.constants import (
    ALLOWED_SPECIES,
    MEDIUM_ROOM_MAX_WEIGHT,
    MIN_AGE_MONTHS,
    SIZE_LARGE,
    SIZE_MEDIUM,
    SIZE_SMALL,
    SMALL_ROOM_MAX_WEIGHT,
)
from users.models import User


class Pet(models.Model):
    """Питомец, которого владелец оставляет в гостинице"""

    name = models.CharField(max_length=100, verbose_name="Кличка")
    species = models.CharField(
        max_length=50,
        verbose_name="Вид",
        help_text="Гостиница принимает кошек и собак",
    )
    age_months = models.PositiveIntegerField(
        verbose_name="Возраст, мес.",
        help_text="Принимаем питомцев от 3 месяцев",
    )
    weight_kg = models.FloatField(
        validators=[MinValueValidator(0.1)],
        verbose_name="Вес, кг",
        help_text="По весу подбирается размер места",
    )
    is_vaccinated = models.BooleanField(
        default=False,
        verbose_name="Есть прививки",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="pets",
        verbose_name="Владелец",
    )

    class Meta:
        """Порядок, названия и ограничения таблицы питомцев"""

        ordering = ["name"]
        verbose_name = "Питомец"
        verbose_name_plural = "Питомцы"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(weight_kg__gt=0),
                name="pet_weight_positive",
            ),
        ]

    def __str__(self) -> str:
        """Вернуть кличку питомца"""
        return self.name

    def get_absolute_url(self) -> str:
        """Адрес страницы питомца на сайте"""
        return reverse("pets:detail", kwargs={"pet_id": self.pk})

    def rejection_reason(self) -> str:
        """Вернуть причину отказа или пустую строку, если отказа нет"""
        if self.species not in ALLOWED_SPECIES:
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
