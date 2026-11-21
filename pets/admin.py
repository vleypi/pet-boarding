from django.contrib import admin

from bookings.models import Booking
from db.search import CyrillicSearchMixin
from pets.models import Pet


class PetBookingInline(admin.TabularInline):
    """История бронирований питомца внутри его карточки"""

    model = Booking
    fields = ("room", "check_in", "check_out", "status")
    autocomplete_fields = ("room",)
    extra = 0
    show_change_link = True


@admin.register(Pet)
class PetAdmin(CyrillicSearchMixin, admin.ModelAdmin):
    """Список и карточка питомцев в административной панели"""

    list_display = ("id", "name", "species", "age_months", "weight_kg",
                    "room_size", "is_vaccinated", "owner", "acceptance")
    list_display_links = ("id", "name")
    list_filter = ("species", "room_size", "is_vaccinated")
    search_fields = ("name", "owner__name")
    list_select_related = ("owner",)
    autocomplete_fields = ("owner",)
    ordering = ("name",)
    list_per_page = 20
    inlines = (PetBookingInline,)

    @admin.display(description="Допуск")
    def acceptance(self, obj: Pet) -> str:
        """Можно ли принять питомца или причина отказа"""
        return obj.rejection_reason() or "можно принять"
