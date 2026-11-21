from django.db.models import Q


def case_variants(query: str) -> set[str]:
    """Варианты регистра строки, нужные SQLite для поиска по кириллице"""
    return {query, query.lower(), query.upper(), query.capitalize(),
            query.title()}


def text_search(query: str, *fields: str) -> Q:
    """Условие поиска подстроки без учёта регистра по нескольким полям"""
    condition = Q()
    for field in fields:
        for variant in case_variants(query):
            condition |= Q(**{f"{field}__icontains": variant})
    return condition


class CyrillicSearchMixin:
    """Поиск в административной панели без учёта регистра кириллицы"""

    def get_search_results(self, request, queryset, search_term):
        """Отфильтровать записи по search_fields через text_search"""
        search_term = search_term.strip()
        if not search_term:
            return queryset, False
        condition = text_search(search_term, *self.search_fields)
        return queryset.filter(condition), False
