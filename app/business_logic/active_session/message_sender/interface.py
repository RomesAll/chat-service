from abc import ABC, abstractmethod
from app.shared.dtos import BaseMessageDtoPostRequest


class IMessageRoute(ABC):
    """
    Класс интерфейс для типов сообщений
    """

    @abstractmethod
    async def send_message(self, message_send_request: BaseMessageDtoPostRequest):
        """Отправка сообщения"""
        pass