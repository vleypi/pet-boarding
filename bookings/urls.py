from django.urls import path

from bookings import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_list, name="list"),
    path("create/", views.booking_create, name="create"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:booking_id>/", views.booking_detail, name="detail"),
    path("<int:booking_id>/edit/", views.booking_update, name="update"),
    path("<int:booking_id>/cancel/", views.booking_cancel, name="cancel"),
]
