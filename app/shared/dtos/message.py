from enum import Enum
from uuid import UUID
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostRequest,
    BaseDtoUpdateRequest, BaseDtoDeleteRequest
)


class PrivateMessageDtoGetResponse(BaseDtoGetResponse):
    """Dto модель для хранения полученной информации о приватных сообщениях"""
    sender_id: UUID
    recipient_id: UUID
    message: str
    type: MessageType


class GroupMessageDtoGetResponse(BaseDtoGetResponse):
    """Dto модель для хранения полученной информации о групповых сообщениях"""
    sender_id: UUID
    chat_id: UUID
    message: str
    type: MessageType


class PrivateMessageDtoPostRequest(BaseDtoPostRequest):
    """Dto модель для хранения данных о приватных сообщениях для сохранения"""
    sender_id: UUID
    recipient_id: UUID
    message: str
    type: MessageType


class GroupMessageDtoPostRequest(BaseDtoPostRequest):
    """Dto модель для хранения данных о групповых сообщениях для сохранения"""
    sender_id: UUID
    chat_id: UUID
    message: str
    type: MessageType


class MessageDtoUpdateRequest(BaseDtoUpdateRequest):
    """Dto модель для хранения данных о приватных и групповых сообщении для обновления"""
    message: str
    is_deleted: bool


class MessageDtoDeleteRequest(BaseDtoDeleteRequest):
    """Dto модель для хранения данных о сообщениях для удаления"""
    pass


class MessageType(str, Enum):
    PRIVATE = 'private'
    GROUP = 'group'
