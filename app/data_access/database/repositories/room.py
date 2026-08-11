from sqlalchemy.orm import Session
from models.room import RoomOrm
from .base import BaseRepository
from app.shared.dtos import (
    BaseDtoClientRequest,
    RoomDtoPostRequest,
    RoomDtoGetResponse
)


class RoomRepository(
    BaseRepository[BaseDtoClientRequest, RoomDtoGetResponse, RoomDtoPostRequest]
):
    """Репозиторий для работы с данными групп"""

    def __init__(self, session: Session):
        super().__init__(session=session)
        self.dto_response = RoomDtoGetResponse
        self.model = RoomOrm