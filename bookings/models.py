from datetime import date

from django.db import models

from pets.models import Pet
from rooms.models import Room
from src.constants import STATUS_ACTIVE, STATUS_CANCELLED
from src.models.common import count_nights


class Booking(models.Model):
    """Бронирование места для питомца на период проживания"""

    pet = models.ForeignKey(
        Pet,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Питомец",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Место",
    )
    check_in = models.DateField(verbose_name="Дата заезда")
    check_out = models.DateField(verbose_name="Дата выезда")
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name="Отменено",
    )

    class Meta:
        """Порядок, названия и ограничения таблицы бронирований"""

        ordering = ["check_in", "pk"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(check_out__gt=models.F("check_in")),
                name="booking_check_out_after_check_in",
            ),
        ]

    def __str__(self) -> str:
        """Вернуть питомца, место и период бронирования"""
        return (
            f"{self.pet}, {self.room}, "
            f"с {self.check_in} по {self.check_out}"
        )

    @property
    def status(self) -> str:
        """Текстовое состояние бронирования"""
        if self.is_cancelled:
            return STATUS_CANCELLED
        return STATUS_ACTIVE

    @property
    def nights(self) -> int:
        """Число суток проживания"""
        return count_nights(self.check_in, self.check_out)

    @property
    def cost(self) -> int:
        """Стоимость проживания по тарифу места"""
        return self.room.cost_for(self.check_in, self.check_out)

    def overlaps(self, check_in: date, check_out: date) -> bool:
        """Проверить, пересекается ли бронирование с периодом"""
        return self.check_in < check_out and check_in < self.check_out

    def cancel(self) -> None:
        """Отменить бронирование и сохранить только признак отмены"""
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])
