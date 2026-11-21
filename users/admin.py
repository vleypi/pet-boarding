from django.contrib import admin
from django.db.models import Count

from db.search import CyrillicSearchMixin
from pets.models import Pet
from users.models import User


class PetInline(admin.TabularInline):
    """Питомцы владельца внутри его карточки"""

    model = Pet
    fields = ("name", "species", "age_months", "weight_kg",
              "is_vaccinated")
    extra = 0
    show_change_link = True


@admin.register(User)
class UserAdmin(CyrillicSearchMixin, admin.ModelAdmin):
    """Список и карточка пользователей предметной области"""

    list_display = ("id", "name", "phone", "role", "pets_count")
    list_display_links = ("id", "name")
    list_filter = ("role",)
    search_fields = ("name", "phone")
    ordering = ("name",)
    list_per_page = 20
    inlines = (PetInline,)

    def get_queryset(self, request):
        """Добавить к пользователям число питомцев"""
        return super().get_queryset(request).annotate(
            pets_total=Count("pets")
        )

    @admin.display(description="Питомцев", ordering="pets_total")
    def pets_count(self, obj: User) -> int:
        """Число питомцев пользователя"""
        return obj.pets_total
