from abc import ABC, abstractmethod
from starlette.websockets import WebSocket
from shared.dtos.message import BaseMessageDtoPostRequest


class IMessageRoute(ABC):
    """
    Класс интерфейс для типов сообщений
    """

    @abstractmethod
    async def send_message(self, message_request: BaseMessageDtoPostRequest, connections: set[WebSocket]):
        """Отправка сообщения"""
        pass