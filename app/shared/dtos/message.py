from enum import Enum
from uuid import UUID
from pydantic import Field
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostDeleteRequest,
    BaseDtoPutPathRequest,
)


class MessageType(str, Enum):
    """Перечисление для типов сообщений"""
    PRIVATE = 'private'
    GROUP = 'group'


class BaseMessageDtoGetResponse(BaseDtoGetResponse):
    """Базовый Message DTO для операции получения (Get) информации о сообщении"""
    sender_id: str
    message: str
    type: MessageType


class PrivateMessageDtoGetResponse(BaseMessageDtoGetResponse):
    """Private message_sender DTO для операции получения (Get) информации о приватных сообщениях"""
    recipient_id: str
    type: MessageType = Field(MessageType.PRIVATE)


class GroupMessageDtoGetResponse(BaseMessageDtoGetResponse):
    """Group message_sender DTO для операции получения (Get) информации о групповых сообщениях"""
    chat_id: UUID
    type: MessageType = Field(MessageType.GROUP)


class BaseMessageDtoPostRequest(BaseDtoPostDeleteRequest):
    """Базовый Message DTO для операции добавления (Post) информации о сообщении"""
    sender_id: str
    message: str
    type: MessageType


class PrivateMessageDtoPostRequest(BaseMessageDtoPostRequest):
    """Private message_sender DTO для операции добавления (Post) информации о приватных сообщениях"""
    recipient_id: str
    type: MessageType = Field(MessageType.PRIVATE)


class GroupMessageDtoPostRequest(BaseMessageDtoPostRequest):
    """Group message_sender DTO для операции добавления (Post) информации о групповых сообщениях"""
    chat_id: UUID
    type: MessageType = Field(MessageType.GROUP)


class MessageDtoUpdateRequest(BaseDtoPutPathRequest):
    """Message DTO для операции обновления (Put) информации о сообщении"""
    message: str
    is_deleted: bool


class MessageDtoDeleteRequest(BaseDtoPostDeleteRequest):
    """Message DTO для операции удаления (Delete) информации о сообщении"""
    pass