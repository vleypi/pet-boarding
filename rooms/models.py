from datetime import date

from django.core.validators import MinValueValidator
from django.db import models

from src.constants import ROOM_SIZES
from src.models.common import count_nights


class Room(models.Model):
    """Место в гостинице: вольер или комната определённого размера"""

    SIZE_CHOICES = [(size, size) for size in ROOM_SIZES]

    name = models.CharField(max_length=100, verbose_name="Название")
    size = models.CharField(
        max_length=20,
        choices=SIZE_CHOICES,
        verbose_name="Размер",
        help_text="Малое до 5 кг, среднее до 20 кг, большое от 20 кг",
    )
    price_per_night = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Тариф за сутки, руб.",
        help_text="Целое число рублей больше нуля",
    )

    class Meta:
        """Порядок, названия и ограничения таблицы мест"""

        ordering = ["name"]
        verbose_name = "Место"
        verbose_name_plural = "Места"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(size__in=ROOM_SIZES),
                name="room_size_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(price_per_night__gt=0),
                name="room_price_positive",
            ),
        ]

    def __str__(self) -> str:
        """Вернуть название места"""
        return self.name

    def is_suitable_for(self, pet) -> bool:
        """Проверить, подходит ли место питомцу по размеру"""
        return self.size == pet.required_room_size()

    def cost_for(self, check_in: date, check_out: date) -> int:
        """Посчитать стоимость проживания в месте за период"""
        return count_nights(check_in, check_out) * self.price_per_night
