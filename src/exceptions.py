class BookingError(Exception):
    """Общая ошибка оформления бронирования"""


class InvalidPeriodError(BookingError):
    """Дата выезда не позже даты заезда"""


class PetNotAcceptedError(BookingError):
    """Питомец не проходит условия приёма"""


class RoomNotSuitableError(BookingError):
    """Место не подходит питомцу по размеру"""


class RoomNotAvailableError(BookingError):
    """Место занято на выбранные даты"""
