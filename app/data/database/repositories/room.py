from sqlalchemy.orm import Session
from app.services.dtos.room import RoomDtoGetResponse
from models.room import RoomOrm
from .base import BaseRepository


class RoomRepository(BaseRepository):
    """Репозиторий для работы с данными групп"""
    def __init__(self, session: Session):
        super().__init__(
            dto_response=RoomDtoGetResponse,
            session=session,
            model=RoomOrm
        )