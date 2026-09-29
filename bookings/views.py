from django.http import HttpRequest, HttpResponse


def booking_list(request: HttpRequest) -> HttpResponse:
    """Список бронирований"""
    return HttpResponse("Список бронирований")


def booking_detail(request: HttpRequest, booking_id: int) -> HttpResponse:
    """Страница бронирования"""
    return HttpResponse(f"Бронирование {booking_id}")
