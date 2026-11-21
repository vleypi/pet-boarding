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
