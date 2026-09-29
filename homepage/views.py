from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from homepage.layout import SECTIONS, page
from src.constants import (
    ALLOWED_SPECIES,
    MEDIUM_ROOM_MAX_WEIGHT,
    MIN_AGE_MONTHS,
    SIZE_LARGE,
    SIZE_MEDIUM,
    SIZE_SMALL,
    SMALL_ROOM_MAX_WEIGHT,
)


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
