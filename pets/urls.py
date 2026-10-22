from django.urls import path

from pets import views

app_name = "pets"

urlpatterns = [
    path("", views.pet_list, name="list"),
    path("<int:pet_id>/", views.pet_detail, name="detail"),
]
