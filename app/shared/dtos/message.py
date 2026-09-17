from enum import Enum
from typing import Any
from uuid import UUID
from pydantic import Field, BaseModel, ConfigDict, model_validator
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostDeleteRequest, BaseDtoPutPathRequest,
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
    is_read: bool = False
    reply_to_message_id: UUID | None = None
    forwarded_from_message_id: UUID | None = None
    forwarded_from_user_id: str | None = None


class PrivateMessageDtoPostRequest(
    BaseMessageDtoWithSenderInfo, BaseMessageDtoWithRecipientInfo, BaseDtoPostDeleteRequest
):
    """DTO для операции добавления (Post) информации о приватных сообщениях"""
    id: UUID
    reply_to_message_id: UUID | None = None
    forwarded_from_message_id: UUID | None = None
    forwarded_from_user_id: str | None = None


class PrivateMessageDtoUpdateRequest(BaseDtoPutPathRequest):
    """DTO для операции обновления (Put) информации о сообщении"""
    is_read: bool | None = Field(default=None, examples=[None])
    message_for_recipient: str | None = Field(default=None, examples=[None])
    message_for_sender: str | None = Field(default=None, examples=[None])
    recipient_key_version: str | None = Field(default=None, examples=[None])
    sender_key_version: str | None = Field(default=None, examples=[None])

    @model_validator(mode='after')
    def integrity_data(self):
        content_field = [
            self.message_for_recipient,
            self.message_for_sender,
            self.recipient_key_version,
            self.sender_key_version
        ]
        field_not_none = [field for field in content_field if field is not None]
        if field_not_none and len(field_not_none) != 4:
            raise ValueError(
                'Для обновления сообщения нужно заполнить все 4 поля: '
                'message_for_recipient, message_for_sender, '
                'recipient_key_version, sender_key_version'
            )
        return self


class GroupMessageDtoUpdateRequest(BaseDtoPutPathRequest):
    """DTO для операции обновления (Put) информации о групповых сообщений"""
    is_read: bool | None = Field(default=None, examples=[None])
    payload: dict[str, Any] | None = Field(default=None, examples=[None])