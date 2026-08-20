from abc import ABC, abstractmethod
from uuid import UUID

from dtos import MessageAttachmentsDtoPostRequest
from dtos.message import BaseMessageDto


class IMessageRoute(ABC):
    """
    Класс интерфейс для типов сообщений
    """

    @abstractmethod
    async def send_message(self, session_id: UUID, message_send_request: BaseMessageDto):
        """Отправка сообщения"""
        pass