from django.urls import path

from bookings import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_list, name="list"),
    path("<int:booking_id>/", views.booking_detail, name="detail"),
]
