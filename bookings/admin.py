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
                    "nights", "cost", "is_cancelled")
    list_display_links = ("id", "pet")
    list_filter = ("is_cancelled", "room__size", "room")
    search_fields = ("pet__name", "pet__owner__name", "room__name")
    list_select_related = ("pet__owner", "room")
    autocomplete_fields = ("pet", "room")
    readonly_fields = ("nights", "cost")
    date_hierarchy = "check_in"
    ordering = ("-check_in",)
    list_per_page = 20
    actions = ("cancel_selected", "restore_selected")

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
        """Отметить выбранные бронирования отменёнными"""
        updated = queryset.filter(is_cancelled=False).update(
            is_cancelled=True
        )
        self.message_user(request, f"Отменено бронирований: {updated}",
                          messages.SUCCESS)

    @admin.action(description="Вернуть выбранные в активные")
    def restore_selected(self, request, queryset) -> None:
        """Снять отметку отмены у выбранных бронирований"""
        updated = queryset.filter(is_cancelled=True).update(
            is_cancelled=False
        )
        self.message_user(request, f"Возвращено в активные: {updated}",
                          messages.SUCCESS)
