from enum import Enum
from uuid import UUID
from pydantic import ConfigDict
from starlette.websockets import WebSocket

from .base import (
    BaseDtoOrmRecordGetResponse,
    BaseDtoOrmRecordPostRequest,
    BaseDtoOrmRecordPutResponse,
    BaseDtoOrmRecordDeleteResponse
)


class MessageType(str, Enum):
    """Перечисление для типов сообщений"""
    PRIVATE = 'private'
    GROUP = 'group'


class BaseMessageDtoGetResponse(BaseDtoOrmRecordGetResponse):
    """Базовый Message DTO для операции получения (Get) информации о сообщении"""
    sender_id: UUID
    message: str
    type: MessageType


class PrivateMessageDtoGetResponse(BaseMessageDtoGetResponse):
    """Private message_sender DTO для операции получения (Get) информации о приватных сообщениях"""
    recipient_id: UUID


class GroupMessageDtoGetResponse(BaseMessageDtoGetResponse):
    """Group message_sender DTO для операции получения (Get) информации о групповых сообщениях"""
    chat_id: UUID


class BaseMessageDtoPostRequest(BaseDtoOrmRecordPostRequest):
    """Базовый Message DTO для операции добавления (Post) информации о сообщении"""
    sender_id: UUID
    message: str
    type: MessageType


class PrivateMessageDtoPostRequest(BaseMessageDtoPostRequest):
    """Private message_sender DTO для операции добавления (Post) информации о приватных сообщениях"""
    recipient_id: UUID


class GroupMessageDtoPostRequest(BaseMessageDtoPostRequest):
    """Group message_sender DTO для операции добавления (Post) информации о групповых сообщениях"""
    chat_id: UUID


class MessageDtoUpdateRequest(BaseDtoOrmRecordPutResponse):
    """Message DTO для операции обновления (Put) информации о сообщении"""
    message: str
    is_deleted: bool


class MessageDtoDeleteRequest(BaseDtoOrmRecordDeleteResponse):
    """Message DTO для операции удаления (Delete) информации о сообщении"""
    pass


class BaseMessageDtoSend(BaseMessageDtoPostRequest):
    connections: set[WebSocket]
    model_config = ConfigDict(arbitrary_types_allowed=True)


class GroupMessageDtoSend(BaseMessageDtoSend):
    """Message DTO для broadcast сообщений"""
    chat_id: UUID


class PrivateMessageDtoSend(BaseMessageDtoSend):
    """Message DTO для broadcast сообщений"""
    recipient_id: UUID