from uuid import UUID
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostRequest,
    BaseDtoUpdateRequest
)


class BaseMessageDtoGetResponse(BaseDtoGetResponse):
    """Dto модель для хранения полученной информации о сообщениях"""
    sender_id: UUID
    message: str


class PrivateMessageDtoGetResponse(BaseMessageDtoGetResponse):
    """Dto модель для хранения приватных сообщений пользователей"""
    recipient_id: UUID


class GroupMessageDtoGetResponse(BaseMessageDtoGetResponse):
    """Dto модель для хранения групповых сообщений пользователей"""
    chat_id: UUID


class BaseMessageDtoPostRequest(BaseDtoPostRequest):
    """Dto модель для хранения данных о сообщении для сохранения"""
    sender_id: UUID
    message: str


class PrivateMessageDtoPostRequest(BaseMessageDtoPostRequest):
    """Dto модель для хранения данных о приватных сообщении для сохранения"""
    recipient_id: UUID


class GroupMessageDtoPostRequest(BaseMessageDtoPostRequest):
    """Dto модель для хранения данных о групповых сообщении для сохранения"""
    chat_id: UUID


class MessageDtoUpdateRequest(BaseDtoUpdateRequest):
    """Dto модель для хранения данных о приватных и групповых сообщении для обновления"""
    message: str
    is_deleted: bool

class MessageDtoDeleteRequest(BaseDtoPostRequest):
    """Dto модель для хранения данных о сообщениях для удаления"""
    pass