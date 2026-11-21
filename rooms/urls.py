from django.urls import path

from rooms import views

app_name = "rooms"

urlpatterns = [
    path("", views.room_list, name="list"),
    path("available/", views.available_rooms, name="available"),
    path("<slug:slug>/", views.room_detail, name="detail"),
    path("<slug:slug>/photo/", views.room_photo, name="photo"),
]
