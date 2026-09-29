from django.http import HttpRequest, HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница"""
    return HttpResponse("Передержка домашних животных")
