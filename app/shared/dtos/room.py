from uuid import UUID
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostDeleteRequest,
    BaseDtoPutPathRequest,
)


class RoomDtoGetResponse(BaseDtoGetResponse):
    """Room DTO для операции получения (Get) информации о комнате"""
    name: str


class RoomDtoPostRequest(BaseDtoPostDeleteRequest):
    """Room DTO для операции добавления (Post) информации о комнате"""
    name: str


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


class UserInRoomPostRequest(BaseDtoPostDeleteRequest):
    """User in Room DTO для операции добавления (Post) информации о комнате"""
    id: int | None = None
    user_id: str
    room_id: UUID


class UserInRoomDtoDeleteRequest(BaseDtoPostDeleteRequest):
    """User in Room DTO для операции удаления (Delete) информации о комнате"""
    id: int

