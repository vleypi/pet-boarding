from datetime import date

from django.core.exceptions import ValidationError
from django.db import models

from pets.models import Pet
from rooms.models import Room
from src.models.common import count_nights


class BookingQuerySet(models.QuerySet):
    """Готовые выборки бронирований по статусу, периоду и связям"""

    def active(self):
        """Активные бронирования"""
        return self.filter(status=Booking.Status.ACTIVE)

    def cancelled(self):
        """Отменённые бронирования"""
        return self.filter(status=Booking.Status.CANCELLED)

    def completed(self):
        """Завершённые бронирования"""
        return self.filter(status=Booking.Status.COMPLETED)

    def billable(self):
        """Бронирования, которые приносят выручку: все, кроме отменённых"""
        return self.exclude(status=Booking.Status.CANCELLED)

    def overlapping(self, check_in: date, check_out: date):
        """Активные бронирования, пересекающиеся с периодом"""
        return self.active().filter(
            check_in__lt=check_out,
            check_out__gt=check_in,
        )

    def with_related(self):
        """Загрузить питомца, владельца и место одним запросом"""
        return self.select_related("pet__owner", "room")


class BookingManager(models.Manager.from_queryset(BookingQuerySet)):
    """Менеджер бронирований с методами BookingQuerySet"""


class Booking(models.Model):
    """Бронирование места для питомца на период проживания"""

    class Status(models.TextChoices):
        """Состояния бронирования"""

        ACTIVE = "active", "Активно"
        CANCELLED = "cancelled", "Отменено"
        COMPLETED = "completed", "Завершено"

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
    check_out = models.DateField(
        verbose_name="Дата выезда",
        help_text="Должна быть позже даты заезда",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )

    objects = BookingManager()

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
            models.CheckConstraint(
                condition=models.Q(status__in=["active", "cancelled",
                                               "completed"]),
                name="booking_status_valid",
            ),
        ]

    def __str__(self) -> str:
        """Вернуть питомца, место и период бронирования"""
        return (
            f"{self.pet}, {self.room}, "
            f"с {self.check_in} по {self.check_out}"
        )

    @property
    def is_active(self) -> bool:
        """Бронирование действует и занимает место"""
        return self.status == self.Status.ACTIVE

    @property
    def nights(self) -> int:
        """Число суток проживания, ноль пока даты не заданы"""
        if self.check_in is None or self.check_out is None:
            return 0
        return count_nights(self.check_in, self.check_out)

    @property
    def cost(self) -> int:
        """Стоимость проживания по тарифу места, ноль пока место не выбрано"""
        if self.room_id is None:
            return 0
        return self.nights * self.room.price_per_night

    def overlaps(self, check_in: date, check_out: date) -> bool:
        """Проверить, пересекается ли бронирование с периодом"""
        return self.check_in < check_out and check_in < self.check_out

    def conflicts(self):
        """Другие активные брони того же места на пересекающийся период"""
        return Booking.objects.overlapping(
            self.check_in, self.check_out
        ).filter(room_id=self.room_id).exclude(pk=self.pk)

    def clean(self) -> None:
        """Проверить период, допуск питомца, размер и занятость места"""
        errors = {}
        has_period = self.check_in is not None and self.check_out is not None
        if has_period and self.check_out <= self.check_in:
            errors["check_out"] = "Дата выезда должна быть позже даты заезда"
        if self.pet_id is not None and self.is_active:
            reason = self.pet.rejection_reason()
            if reason:
                errors["pet"] = f"Питомца нельзя принять: {reason}"
            elif self.room_id is not None and not self.room.is_suitable_for(
                self.pet
            ):
                size = self.pet.required_room_size()
                errors["room"] = f"Питомцу нужно {size} место"
        if ("check_out" not in errors and "room" not in errors
                and has_period and self.room_id is not None
                and self.is_active and self.conflicts().exists()):
            errors["room"] = "Место уже занято на эти даты"
        if errors:
            raise ValidationError(errors)

    def cancel(self) -> None:
        """Отменить бронирование и сохранить только статус"""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def complete(self) -> None:
        """Завершить бронирование и сохранить только статус"""
        self.status = self.Status.COMPLETED
        self.save(update_fields=["status"])
