from abc import ABC, abstractmethod
from shared.dtos.message import BaseMessageDtoSend


class IMessageRoute(ABC):
    """
    Класс интерфейс для типов сообщений
    """

    @abstractmethod
    async def send_message(self, message_send_request: BaseMessageDtoSend):
        """Отправка сообщения"""
        pass