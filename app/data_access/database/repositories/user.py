from sqlalchemy.orm import Session
from app.shared.dtos.base import BaseDtoOrmRecord
from app.shared.dtos.user import UserDtoGetResponse, UserDtoPostRequest
from models.user import UserOrm
from .base import BaseRepository


class UserRepository(
    BaseRepository[BaseDtoOrmRecord, UserDtoGetResponse, UserDtoPostRequest]
):
    """Репозиторий для работы с данными пользователей"""

    def __init__(self, session: Session):
        super().__init__(session=session)
        self.dto_response = UserDtoGetResponse
        self.model = UserOrm