from django import forms

from rooms.models import Room

MAX_PHOTO_SIZE = 2 * 1024 * 1024


class RoomPhotoForm(forms.ModelForm):
    """Загрузка фотографии места"""

    class Meta:
        """Только поле фото, остальные данные места не меняются"""

        model = Room
        fields = ["photo"]
        widgets = {
            "photo": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/jpeg,image/png",
            }),
        }

    def clean_photo(self):
        """Проверить, что файл выбран и не больше 2 МБ"""
        photo = self.cleaned_data.get("photo")
        if not photo:
            raise forms.ValidationError("Выберите файл изображения")
        if photo.size > MAX_PHOTO_SIZE:
            raise forms.ValidationError("Файл больше 2 МБ")
        return photo
