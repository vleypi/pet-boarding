from django.urls import path

from rooms import views

urlpatterns = [
    path("", views.room_list, name="room_list"),
    path("<int:room_id>/", views.room_detail, name="room_detail"),
]
