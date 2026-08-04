from sqlalchemy.orm import Session
from app.services.dtos.message import PrivateMessageDtoGetResponse, GroupMessageDtoGetResponse
from models.message import PrivateMessageOrm, GroupMessageOrm
from .base import BaseRepository


class PrivateMessageRepository(BaseRepository):
    """Репозиторий для работы с данными приватных сообщений"""
    def __init__(self, session: Session):
        super().__init__(
            dto_response=PrivateMessageDtoGetResponse,
            session=session,
            model=PrivateMessageOrm
        )


class PublicMessageRepository(BaseRepository):
    """Репозиторий для работы с данными групповых сообщений"""
    def __init__(self, session: Session):
        super().__init__(
            dto_response=GroupMessageDtoGetResponse,
            session=session,
            model=GroupMessageOrm
        )
