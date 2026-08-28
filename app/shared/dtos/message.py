from enum import Enum
from uuid import UUID
from pydantic import Field, BaseModel, ConfigDict
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostDeleteRequest,
)


class MessageType(str, Enum):
    """Перечисление для типов сообщений"""
    PRIVATE_MSG = 'private_msg'
    GROUP_MSG = 'group_msg'


class BaseMessageDto(BaseModel):
    """Базовый DTO для сообщений"""
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseMessageDtoWithSenderInfo(BaseMessageDto):
    """Базовый DTO для сообщений с информацией об отправителе"""
    sender_id: str
    message_for_sender: str | None = None
    sender_key_version: str


class BaseMessageDtoWithRecipientInfo(BaseMessageDto):
    """Базовый DTO для сообщений с информацией о получателе"""
    recipient_id: str
    message_for_recipient: str | None = None
    recipient_key_version: str


class MessageDtoGetResponse(
    BaseMessageDtoWithSenderInfo, BaseMessageDtoWithRecipientInfo, BaseDtoGetResponse
):
    """DTO для операции получения (Get) информации о приватных сообщениях"""
    file_id: list[UUID] = Field(default_factory=list)


class PrivateMessageDtoPostRequest(
    BaseMessageDtoWithSenderInfo, BaseMessageDtoWithRecipientInfo, BaseDtoPostDeleteRequest
):
    """DTO для операции добавления (Post) информации о приватных сообщениях"""
    pass
