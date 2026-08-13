from sqlalchemy import select

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
        self.model: type[UserOrm] = UserOrm

    def get_by_email(self, email: str) -> UserDtoGetResponse:
        stmt = select(self.model).where(self.model.email == email)
        user_info = self.session.execute(stmt).scalar_one()
        return self._get_dto(user_info)

    def save(self, dto_post_request: UserDtoPostRequest) -> UserDtoGetResponse:
        orm_object = self.model(**dto_post_request.model_dump())
        orm_object.password = dto_post_request.password.get_secret_value().encode()
        self.session.add(orm_object)
        self.session.flush()
        return self._get_dto(orm_object)

    def get_hash_psw(self, user_id: str) -> bytes:
        stmt = select(self.model.password).where(self.model.id == user_id)
        password = self.session.execute(stmt).scalar_one_or_none()
        if not password:
            raise Exception
        return password