from sqlalchemy.orm import Session
from dtos.room import UserInRoomDtoGetResponse
from models.room import RoomOrm, UserInRoomOrm
from .base import BaseRepository
from app.shared.dtos import (
    BaseDtoClientRequest,
    RoomDtoPostRequest,
    RoomDtoGetResponse
)


class RoomRepository(
    BaseRepository[BaseDtoClientRequest, RoomDtoGetResponse, RoomDtoPostRequest]
):
    """Репозиторий для работы с данными комнат"""
    def __init__(self, session: Session):
        super().__init__(session=session)
        self.dto_response = RoomDtoGetResponse
        self.model = RoomOrm


class UserInRoomRepository(
    BaseRepository[BaseDtoClientRequest, RoomDtoGetResponse, RoomDtoPostRequest]
):
    """Репозиторий для работы с данными пользователей в комнате"""
    def __init__(self, session: Session):
        super().__init__(session=session)
        self.dto_response = UserInRoomDtoGetResponse
        self.model = UserInRoomOrm