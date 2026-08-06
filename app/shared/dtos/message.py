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


class BaseMessageDtoPostRequest(BaseDtoPostRequest):
    """Базовая dto модель для приватных и групповых сообщений"""
    sender_id: UUID
    message: str
    type: MessageType


class PrivateMessageDtoPostRequest(BaseMessageDtoPostRequest):
    """Dto модель для хранения данных о приватных сообщениях для сохранения"""
    recipient_id: UUID


class GroupMessageDtoPostRequest(BaseMessageDtoPostRequest):
    """Dto модель для хранения данных о групповых сообщениях для сохранения"""
    chat_id: UUID


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
