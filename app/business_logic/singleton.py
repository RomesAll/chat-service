from threading import Lock
from typing import Self


class Singleton:
    """Класс для создания потокобезопасных singleton объектов"""
    _instance: dict = {}
    _lock = Lock()

    def __new__(cls, *args, **kwargs) -> Self:
        if not cls._instance.get(cls, None):
            with cls._lock:
                if not cls._instance.get(cls, None):
                    cls._instance[cls] = super().__new__(cls)
        if cls._instance.get(cls, None):
            return cls._instance[cls]
        else:
            raise Exception(f'Ошибка создание singleton для {cls.__name__}')

    def __init__(self):
        if hasattr(self, '_is_init'):
            return