from uuid import UUID
from pydantic import BaseModel
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostDeleteRequest,
    BaseDtoPutPathRequest,
)


class RoomDtoGetResponse(BaseDtoGetResponse):
    """Room DTO для операции получения (Get) информации о комнате"""
    name: str
    owner: str


class RoomDtoPostRequest(BaseDtoPostDeleteRequest):
    """Room DTO для операции добавления (Post) информации о комнате"""
    id: UUID
    name: str
    owner: str


class RoomDtoUpdateRequest(RoomDtoPostRequest, BaseDtoPutPathRequest):
    """Room DTO для операции обновления (Put) информации о комнате"""
    pass


class RoomDtoDeleteRequest(BaseDtoPostDeleteRequest):
    """Room DTO для операции удаления (Delete) информации о комнате"""
    pass


class UserInRoomResponse(BaseDtoGetResponse):
    """Dto для получения информации о составе группы"""
    id: int
    user_id: str
    room_id: UUID

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UserInRoomResponse):
            return self.user_id == other.user_id
        if isinstance(other, str):
            return self.user_id == other
        return NotImplemented


class UserInRoomPostRequest(BaseDtoPostDeleteRequest):
    """User in Room DTO для операции добавления (Post) информации о комнате"""
    user_id: str
    room_id: UUID


class UserInRoomDtoDeleteRequest(BaseDtoPostDeleteRequest):
    """User in Room DTO для операции удаления (Delete) информации о комнате"""
    id: int


class GenerateUrlInviteRoomRequest(BaseModel):
    """DTO для генерации url для добавления в комнату"""
    room_id: UUID
    created_by: str
    max_uses: int | None = None
    hours: int = 24