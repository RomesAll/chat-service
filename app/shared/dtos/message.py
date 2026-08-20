from enum import Enum
from uuid import UUID
from pydantic import Field, BaseModel, ConfigDict
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostDeleteRequest,
)


class MessageType(str, Enum):
    """Перечисление для типов сообщений"""
    TEXT = 'text'
    VIDEO = 'video'


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


class PrivateMessageDtoGetResponse(
    BaseMessageDtoWithSenderInfo, BaseMessageDtoWithRecipientInfo, BaseDtoGetResponse
):
    """DTO для операции получения (Get) информации о приватных сообщениях"""
    file_id: list[UUID] = Field(default_factory=list)


class PrivateMessageDtoPostRequest(
    BaseMessageDtoWithSenderInfo, BaseMessageDtoWithRecipientInfo, BaseDtoPostDeleteRequest
):
    """DTO для операции добавления (Post) информации о приватных сообщениях"""
    pass


# class PrivateMsgDtoPhotoRequest(PrivateMessageDtoPostRequest):
#     pass
#
#
# class PrivateMsgDtoPostRequest(PrivateMsgDtoPhotoRequest):
#     pass
#
#
# class MessageDtoUpdateRequest(BaseDtoPutPathRequest):
#     """Message DTO для операции обновления (Put) информации о сообщении"""
#     message: str
#     is_deleted: bool
#     user_keys_version: datetime
#
#
# class MessageDtoDeleteRequest(BaseDtoPostDeleteRequest):
#     """Message DTO для операции удаления (Delete) информации о сообщении"""
#     pass