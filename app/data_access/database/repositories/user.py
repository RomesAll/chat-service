from sqlalchemy.orm import Session
from models.user import UserOrm
from .exception_handler import HandleSqlAlchemyException
from .base import BaseRepository
from app.shared.dtos import (
    UserDtoGetResponse,
    UserDtoPostRequest,
    BaseDtoClientRequest
)


@HandleSqlAlchemyException()
class UserRepository(
    BaseRepository[BaseDtoClientRequest, UserDtoGetResponse, UserDtoPostRequest]
):
    """Репозиторий для работы с данными пользователей"""

    def __init__(self, session: Session):
        super().__init__(session=session)
        self.dto_response = UserDtoGetResponse
        self.model = UserOrm

    def save(self, dto_post_request: UserDtoPostRequest) -> UserDtoGetResponse:
        orm_object = self.model(**dto_post_request.model_dump())
        orm_object.password = dto_post_request.password.get_secret_value().encode()
        self.session.add(orm_object)
        self.session.flush()
        return self._get_dto(orm_object)