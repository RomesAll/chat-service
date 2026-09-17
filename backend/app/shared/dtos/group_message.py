from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import Field
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostDeleteRequest,
)


class GroupMessageDtoResponse(BaseDtoGetResponse):
    """Room DTO для операции получения (Get) информации о групповых сообщениях"""
    room_id: UUID
    sender_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    time_send: datetime
    file_id: list[UUID] = Field(default_factory=list)
    is_read: bool = False
    reply_to_message_id: UUID | None = None
    forwarded_from_message_id: UUID | None = None
    forwarded_from_user_id: str | None = None
    forwarded_from_room_id: UUID | None = None

class GroupMessageDtoPostRequest(BaseDtoPostDeleteRequest):
    """Room DTO для операции добавления (Post) информации о групповых сообщениях"""
    id: UUID
    room_id: UUID
    sender_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    reply_to_message_id: UUID | None = None
    forwarded_from_message_id: UUID | None = None
    forwarded_from_user_id: str | None = None
    forwarded_from_room_id: UUID | None = None


class GroupMessageDtoDeleteRequest(BaseDtoPostDeleteRequest):
    """Room DTO для операции удаления (Delete) информации о комнате"""
    pass