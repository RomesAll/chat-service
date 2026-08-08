from sqlalchemy.orm import Session
from app.shared.dtos.room import RoomDtoGetResponse
from models.room import RoomOrm
from shared.dtos.base import BaseDtoOrmRecord
from shared.dtos.room import RoomDtoPostRequest
from .base import BaseRepository


class RoomRepository(
    BaseRepository[BaseDtoOrmRecord, RoomDtoGetResponse, RoomDtoPostRequest]
):
    """Репозиторий для работы с данными групп"""

    def __init__(self, session: Session):
        super().__init__(session=session)
        self.dto_response = RoomDtoGetResponse
        self.model = RoomOrm