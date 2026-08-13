from uuid import UUID
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostDeleteRequest,
    BaseDtoPutPathRequest,
    BaseModelWithPrint,
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


class InvitationUserInRoomDtoRequest(BaseModelWithPrint):
    """DTO для добавления пользователя в комнату"""
    room_id: UUID
    user_id: str

class UserInRoomDtoGetResponse(InvitationUserInRoomDtoRequest, BaseDtoGetResponse):
    pass

