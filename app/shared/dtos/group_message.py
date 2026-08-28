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


class GroupMessageDtoPostRequest(BaseDtoPostDeleteRequest):
    """Room DTO для операции добавления (Post) информации о групповых сообщениях"""
    room_id: UUID
    sender_id: str
    payload: dict[str, Any] = Field(default_factory=dict)


class GroupMessageDtoDeleteRequest(BaseDtoPostDeleteRequest):
    """Room DTO для операции удаления (Delete) информации о комнате"""
    pass