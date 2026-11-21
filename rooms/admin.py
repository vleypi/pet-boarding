from django.contrib import admin
from django.db.models import Count, Q

from bookings.models import Booking
from db.search import CyrillicSearchMixin
from rooms.models import Room


class BookingInline(admin.TabularInline):
    """Бронирования места внутри его карточки"""

    model = Booking
    fields = ("pet", "check_in", "check_out", "is_cancelled")
    autocomplete_fields = ("pet",)
    extra = 0
    show_change_link = True


@admin.register(Room)
class RoomAdmin(CyrillicSearchMixin, admin.ModelAdmin):
    """Список и карточка мест в административной панели"""

    list_display = ("id", "name", "size", "price_per_night",
                    "active_bookings")
    list_display_links = ("id", "name")
    list_editable = ("price_per_night",)
    list_filter = ("size",)
    search_fields = ("name",)
    ordering = ("price_per_night", "name")
    list_per_page = 20
    inlines = (BookingInline,)

    def get_queryset(self, request):
        """Добавить к местам число активных бронирований одним запросом"""
        return super().get_queryset(request).annotate(
            active_count=Count(
                "bookings", filter=Q(bookings__is_cancelled=False)
            )
        )

    @admin.display(description="Активных броней",
                   ordering="active_count")
    def active_bookings(self, obj: Room) -> int:
        """Число активных бронирований места"""
        return obj.active_count
