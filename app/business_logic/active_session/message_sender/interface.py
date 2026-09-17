from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.shared.dtos import GroupMessageDtoResponse, MessageDtoGetResponse, BaseDtoGetResponse


class IMessageRoute(ABC):
    """
    Класс интерфейс для типов сообщений
    """

    @abstractmethod
    async def send_message(self, session_id: UUID, message_send_response: Any):
        """Отправка сообщения"""
        pass