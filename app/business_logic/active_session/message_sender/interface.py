from abc import ABC, abstractmethod


class IMessageRoute(ABC):
    """
    Класс интерфейс для типов сообщений
    """

    @abstractmethod
    async def send_message(self, *args, **kwargs):
        """Отправка сообщения"""
        pass