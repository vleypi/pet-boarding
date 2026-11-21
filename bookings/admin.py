from django.contrib import admin, messages

from bookings.models import Booking
from db.search import CyrillicSearchMixin

admin.site.site_header = "Передержка домашних животных"
admin.site.site_title = "Передержка: администрирование"
admin.site.index_title = "Управление данными гостиницы"


@admin.register(Booking)
class BookingAdmin(CyrillicSearchMixin, admin.ModelAdmin):
    """Список и карточка бронирований в административной панели"""

    list_display = ("id", "pet", "owner", "room", "check_in", "check_out",
                    "nights", "cost", "status")
    list_display_links = ("id", "pet")
    list_filter = ("status", "room__size", "room")
    search_fields = ("pet__name", "pet__owner__name", "room__name")
    list_select_related = ("pet__owner", "room")
    autocomplete_fields = ("pet", "room")
    readonly_fields = ("nights", "cost")
    date_hierarchy = "check_in"
    ordering = ("-check_in",)
    list_per_page = 20
    actions = ("cancel_selected", "complete_selected", "restore_selected")

    @admin.display(description="Владелец", ordering="pet__owner__name")
    def owner(self, obj: Booking) -> str:
        """Владелец питомца"""
        return obj.pet.owner.name

    @admin.display(description="Суток")
    def nights(self, obj: Booking) -> int:
        """Число суток проживания"""
        return obj.nights

    @admin.display(description="Стоимость, руб.")
    def cost(self, obj: Booking) -> int:
        """Стоимость проживания"""
        return obj.cost

    @admin.action(description="Отменить выбранные бронирования")
    def cancel_selected(self, request, queryset) -> None:
        """Отметить выбранные активные бронирования отменёнными"""
        updated = queryset.active().update(status=Booking.Status.CANCELLED)
        self.message_user(request, f"Отменено бронирований: {updated}",
                          messages.SUCCESS)

    @admin.action(description="Завершить выбранные бронирования")
    def complete_selected(self, request, queryset) -> None:
        """Отметить выбранные активные бронирования завершёнными"""
        updated = queryset.active().update(status=Booking.Status.COMPLETED)
        self.message_user(request, f"Завершено бронирований: {updated}",
                          messages.SUCCESS)

    @admin.action(description="Вернуть выбранные в активные")
    def restore_selected(self, request, queryset) -> None:
        """Вернуть бронирования в активные, если место свободно"""
        restored, skipped = 0, []
        for booking in queryset.exclude(status=Booking.Status.ACTIVE):
            booking.status = Booking.Status.ACTIVE
            if booking.conflicts().exists():
                skipped.append(str(booking.pk))
                continue
            booking.save(update_fields=["status"])
            restored += 1
        self.message_user(request, f"Возвращено в активные: {restored}",
                          messages.SUCCESS)
        if skipped:
            self.message_user(
                request,
                "Место занято, не возвращены: " + ", ".join(skipped),
                messages.WARNING,
            )
