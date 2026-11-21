from datetime import timedelta

from django import forms
from django.utils import timezone

from bookings.models import Booking
from pets.models import Pet
from rooms.models import Room
from src.constants import ROOM_SIZES

SORT_FIELDS = {
    "check_in": ("check_in", "pk"),
    "-check_in": ("-check_in", "-pk"),
    "pet": ("pet__name", "check_in"),
    "owner": ("pet__owner__name", "pet__name", "check_in"),
    "room": ("room__name", "check_in"),
    "price": ("-room__price_per_night", "check_in"),
}
SORT_CHOICES = [
    ("check_in", "сначала ранние заезды"),
    ("-check_in", "сначала поздние заезды"),
    ("pet", "по кличке питомца"),
    ("owner", "по владельцу"),
    ("room", "по месту"),
    ("price", "сначала дорогие места"),
]
DEFAULT_SORT = "check_in"
DATE_INPUT = {"type": "date", "class": "form-control"}


class PetChoiceField(forms.ModelChoiceField):
    """Выбор питомца с видом, весом и владельцем в подписи"""

    def label_from_instance(self, obj: Pet) -> str:
        """Подпись питомца в списке выбора"""
        return (f"{obj.name} ({obj.species}, {obj.weight_kg:g} кг, "
                f"{obj.owner.name})")


class RoomChoiceField(forms.ModelChoiceField):
    """Выбор места с размером и тарифом в подписи"""

    def label_from_instance(self, obj: Room) -> str:
        """Подпись места в списке выбора"""
        return f"{obj.name}: {obj.size}, {obj.price_per_night} ₽ в сутки"


class BookingFilterForm(forms.Form):
    """Параметры поиска, фильтрации и сортировки списка бронирований"""

    q = forms.CharField(
        label="Поиск",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "type": "search",
            "placeholder": "Кличка или владелец",
        }),
    )
    status = forms.ChoiceField(
        label="Статус",
        required=False,
        choices=[("", "все")] + [
            (value, title.lower()) for value, title in Booking.Status.choices
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    size = forms.ChoiceField(
        label="Размер места",
        required=False,
        choices=[("", "любой")] + [(size, size) for size in ROOM_SIZES],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    room = forms.ModelChoiceField(
        label="Место",
        required=False,
        queryset=Room.objects.order_by("name"),
        empty_label="любое",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date_from = forms.DateField(
        label="Заезд с",
        required=False,
        widget=forms.DateInput(attrs=DATE_INPUT, format="%Y-%m-%d"),
    )
    date_to = forms.DateField(
        label="Заезд по",
        required=False,
        widget=forms.DateInput(attrs=DATE_INPUT, format="%Y-%m-%d"),
    )
    sort = forms.ChoiceField(
        label="Сортировка",
        required=False,
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean_q(self) -> str:
        """Убрать пробелы по краям строки поиска"""
        return self.cleaned_data["q"].strip()

    def clean_sort(self) -> str:
        """Подставить сортировку по умолчанию, если она не выбрана"""
        return self.cleaned_data["sort"] or DEFAULT_SORT

    def clean(self) -> dict:
        """Проверить, что начало периода не позже его окончания"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            self.add_error(
                "date_to", "Окончание периода раньше его начала"
            )
            cleaned_data.pop("date_from", None)
        return cleaned_data

    def filters(self) -> dict:
        """Проверенные значения; неверные поля не участвуют в фильтрации"""
        self.is_valid()
        values = {name: self.cleaned_data.get(name) for name in self.fields}
        values["sort"] = values["sort"] or DEFAULT_SORT
        return values


class BookingForm(forms.ModelForm):
    """Создание и изменение бронирования: питомец, место и даты"""

    class Meta:
        """Поля модели, подписи, подсказки и виджеты формы"""

        model = Booking
        fields = ["pet", "room", "check_in", "check_out"]
        field_classes = {"pet": PetChoiceField, "room": RoomChoiceField}
        labels = {
            "pet": "Питомец",
            "room": "Место",
            "check_in": "Дата заезда",
            "check_out": "Дата выезда",
        }
        help_texts = {
            "pet": "Принимаем кошек и собак от 3 месяцев с прививками",
            "room": "Размер места должен подходить питомцу по весу",
            "check_in": "Не раньше сегодняшнего дня",
            "check_out": "Позже даты заезда",
        }
        widgets = {
            "pet": forms.Select(attrs={"class": "form-select"}),
            "room": forms.Select(attrs={"class": "form-select"}),
            "check_in": forms.DateInput(attrs=DATE_INPUT,
                                        format="%Y-%m-%d"),
            "check_out": forms.DateInput(attrs=DATE_INPUT,
                                         format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs) -> None:
        """Отсортировать списки и задать даты по умолчанию для новой брони"""
        super().__init__(*args, **kwargs)
        self.fields["pet"].queryset = Pet.objects.select_related(
            "owner"
        ).order_by("name")
        self.fields["room"].queryset = Room.objects.order_by(
            "price_per_night", "name"
        )
        if self.instance.pk is None and not self.is_bound:
            today = timezone.localdate()
            self.initial.setdefault("check_in", today)
            self.initial.setdefault("check_out", today + timedelta(days=1))

    def clean_check_in(self):
        """Запретить заезд в прошлом, кроме неизменённой даты старой брони"""
        check_in = self.cleaned_data["check_in"]
        unchanged = (self.instance.pk is not None
                     and check_in == self.instance.check_in)
        if check_in < timezone.localdate() and not unchanged:
            raise forms.ValidationError(
                "Нельзя оформить заезд на прошедшую дату"
            )
        return check_in
