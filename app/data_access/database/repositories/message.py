from sqlalchemy.orm import Session
from app.shared.dtos.message import PrivateMessageDtoGetResponse, GroupMessageDtoGetResponse
from models.message import PrivateMessageOrm, GroupMessageOrm
from shared.dtos.base import BaseDtoOrmRecord
from shared.dtos.message import PrivateMessageDtoPostRequest, GroupMessageDtoPostRequest
from .base import BaseRepository


class PrivateMessageRepository(
    BaseRepository[BaseDtoOrmRecord, PrivateMessageDtoGetResponse, PrivateMessageDtoPostRequest]
):
    """Репозиторий для работы с данными приватных сообщений"""

    def __init__(self, session: Session):
        super().__init__(session=session)
        self.dto_response = PrivateMessageDtoGetResponse
        self.model = PrivateMessageOrm


class GroupMessageRepository(
    BaseRepository[BaseDtoOrmRecord, GroupMessageDtoGetResponse, GroupMessageDtoPostRequest]
):
    """Репозиторий для работы с данными групповых сообщений"""

    def __init__(self, session: Session):
        super().__init__(session=session)
        self.dto_response = GroupMessageDtoGetResponse
        self.model = GroupMessageOrm