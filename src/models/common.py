from datetime import date


def next_id(items: list) -> int:
    """Вернуть идентификатор для нового объекта коллекции"""
    return max((item.id for item in items), default=0) + 1


def count_nights(check_in: date, check_out: date) -> int:
    """Посчитать число суток проживания"""
    return (check_out - check_in).days
