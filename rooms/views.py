from django.http import HttpRequest, HttpResponse


def room_list(request: HttpRequest) -> HttpResponse:
    """Список мест"""
    return HttpResponse("Список мест")


def room_detail(request: HttpRequest, room_id: int) -> HttpResponse:
    """Страница места"""
    return HttpResponse(f"Место {room_id}")
