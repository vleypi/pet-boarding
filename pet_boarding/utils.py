"""Ввод данных пользователя с проверкой"""

from datetime import date

YES_ANSWERS = {"да", "д", "yes", "y"}
NO_ANSWERS = {"нет", "н", "no", "n"}


def input_text(prompt: str) -> str:
    """Запросить непустую строку"""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Значение не может быть пустым")


def input_int(prompt: str, minimum: int = 0) -> int:
    """Запросить целое число не меньше указанного"""
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Нужно ввести целое число")
            continue
        if value < minimum:
            print(f"Число не может быть меньше {minimum}")
            continue
        return value


def input_float(prompt: str, minimum: float = 0.0) -> float:
    """Запросить дробное число не меньше указанного"""
    while True:
        try:
            value = float(input(prompt).replace(",", "."))
        except ValueError:
            print("Нужно ввести число, например 4.5")
            continue
        if value < minimum:
            print(f"Число не может быть меньше {minimum}")
            continue
        return value


def input_date(prompt: str) -> date:
    """Запросить дату в формате ГГГГ-ММ-ДД"""
    while True:
        try:
            return date.fromisoformat(input(prompt).strip())
        except ValueError:
            print("Нужна дата в формате ГГГГ-ММ-ДД, например 2026-10-01")


def input_yes_no(prompt: str) -> bool:
    """Запросить ответ да или нет"""
    while True:
        value = input(prompt).strip().lower()
        if value in YES_ANSWERS:
            return True
        if value in NO_ANSWERS:
            return False
        print("Ответьте да или нет")
