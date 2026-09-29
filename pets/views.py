from django.http import HttpRequest, HttpResponse


def pet_list(request: HttpRequest) -> HttpResponse:
    """Список питомцев"""
    return HttpResponse("Список питомцев")


def pet_detail(request: HttpRequest, pet_id: int) -> HttpResponse:
    """Страница питомца"""
    return HttpResponse(f"Питомец {pet_id}")
