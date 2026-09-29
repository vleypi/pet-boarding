from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("rooms/", include("rooms.urls")),
    path("pets/", include("pets.urls")),
    path("bookings/", include("bookings.urls")),
]
