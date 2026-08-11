from sqlalchemy.orm import Session
from models.message import PrivateMessageOrm, GroupMessageOrm
from .base import BaseRepository
from app.shared.dtos import (
    PrivateMessageDtoGetResponse,
    GroupMessageDtoGetResponse,
    BaseDtoClientRequest,
    PrivateMessageDtoPostRequest,
    GroupMessageDtoPostRequest
)


class PrivateMessageRepository(
    BaseRepository[BaseDtoClientRequest, PrivateMessageDtoGetResponse, PrivateMessageDtoPostRequest]
):
    """Репозиторий для работы с данными приватных сообщений"""

    def __init__(self, session: Session):
        super().__init__(session=session)
        self.dto_response = PrivateMessageDtoGetResponse
        self.model = PrivateMessageOrm


class GroupMessageRepository(
    BaseRepository[BaseDtoClientRequest, GroupMessageDtoGetResponse, GroupMessageDtoPostRequest]
):
    """Репозиторий для работы с данными групповых сообщений"""

    def __init__(self, session: Session):
        super().__init__(session=session)
        self.dto_response = GroupMessageDtoGetResponse
        self.model = GroupMessageOrm