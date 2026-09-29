from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import escape

from src.constants import (
    ALLOWED_SPECIES,
    MEDIUM_ROOM_MAX_WEIGHT,
    MIN_AGE_MONTHS,
    SIZE_LARGE,
    SIZE_MEDIUM,
    SIZE_SMALL,
    SMALL_ROOM_MAX_WEIGHT,
)
from src.models import Booking

BOOTSTRAP_CSS = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
)

PAGE_STYLE = """
body { background-color: #fdfaf6; }
.brand { color: #8a4b2d; }
"""

SECTIONS = (
    ("room_list", "Места"),
    ("pet_list", "Питомцы"),
    ("booking_list", "Бронирования"),
)


def navigation() -> str:
    """Собрать ссылки навигации по разделам"""
    return "".join(
        f'<a class="link-secondary" href="{reverse(name)}">{label}</a>'
        for name, label in SECTIONS
    )


def page(title: str, content: str) -> str:
    """Собрать HTML-документ с общим каркасом, стилями и навигацией"""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link rel="stylesheet" href="{BOOTSTRAP_CSS}">
<style>{PAGE_STYLE}</style>
</head>
<body>
<header class="border-bottom bg-white mb-4">
<nav class="container d-flex flex-wrap align-items-center gap-3 py-3">
<a class="brand fw-bold text-decoration-none me-auto"
   href="{reverse("index")}">Передержка</a>
{navigation()}
</nav>
</header>
<main class="container pb-5">{content}</main>
</body>
</html>"""


def format_period(booking: Booking) -> str:
    """Вернуть период проживания с датами в формате ДД.ММ.ГГГГ"""
    return f"с {booking.check_in:%d.%m.%Y} по {booking.check_out:%d.%m.%Y}"


def status_badge(booking: Booking) -> str:
    """Собрать бейдж со статусом бронирования"""
    color = "text-bg-secondary" if booking.is_cancelled else "text-bg-success"
    return f'<span class="badge {color}">{booking.status}</span>'


def object_link(route_name: str, object_id: int, text: str) -> str:
    """Собрать ссылку на страницу объекта с экранированным текстом"""
    url = reverse(route_name, args=[object_id])
    return f'<a href="{url}">{escape(text)}</a>'


def empty_item(text: str) -> str:
    """Собрать пункт списка для пустого набора данных"""
    return f'<li class="list-group-item text-muted">{text}</li>'


def empty_row(columns: int, text: str) -> str:
    """Собрать строку таблицы для пустого набора данных"""
    return f'<tr><td colspan="{columns}" class="text-muted">{text}</td></tr>'


def back_link(route_name: str, label: str) -> str:
    """Собрать кнопку возврата к списку раздела"""
    url = reverse(route_name)
    return f'<a class="btn btn-outline-secondary" href="{url}">{label}</a>'


def not_found(message: str, route_name: str, label: str) -> HttpResponse:
    """Вернуть страницу с сообщением об ошибке и кодом 404"""
    content = f"""
<h1 class="h3 text-danger mb-3">{escape(message)}</h1>
{back_link(route_name, label)}
"""
    return HttpResponse(page(message, content), status=404)


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: описание гостиницы, условия приёма и разделы"""
    buttons = "".join(
        f'<a class="btn btn-primary me-2 mb-2" href="{reverse(name)}">'
        f"{label}</a>"
        for name, label in SECTIONS
    )
    species = " и ".join(sorted(ALLOWED_SPECIES))
    content = f"""
<h1 class="display-5 brand">Передержка домашних животных</h1>
<p class="lead">Гостиница для кошек и собак на время отъезда владельцев.</p>
<div class="mb-4">{buttons}</div>
<div class="row g-3">
<div class="col-md-6">
<div class="card h-100"><div class="card-body">
<h2 class="h5 card-title">Условия приёма</h2>
<ul class="mb-0">
<li>принимаем: {species}</li>
<li>возраст от {MIN_AGE_MONTHS} месяцев</li>
<li>обязательны прививки</li>
</ul>
</div></div>
</div>
<div class="col-md-6">
<div class="card h-100"><div class="card-body">
<h2 class="h5 card-title">Размер места по весу питомца</h2>
<ul class="mb-0">
<li>{SIZE_SMALL}: до {SMALL_ROOM_MAX_WEIGHT} кг</li>
<li>{SIZE_MEDIUM}: от {SMALL_ROOM_MAX_WEIGHT}
до {MEDIUM_ROOM_MAX_WEIGHT} кг</li>
<li>{SIZE_LARGE}: от {MEDIUM_ROOM_MAX_WEIGHT} кг</li>
</ul>
</div></div>
</div>
</div>
"""
    return HttpResponse(page("Передержка домашних животных", content))
