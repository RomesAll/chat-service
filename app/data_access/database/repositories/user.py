from sqlalchemy import select
from app.data_access.exceptions import RecordNotFound
from app.data_access.database.models.user import UserOrm
from .base import BaseRepositoryGet, BaseRepositorySave, BaseRepositoryDelete, BaseRepositoryUpdate
from app.shared.dtos import (
    UserDtoGetResponse,
    UserDtoPostRequest,
)


class UserRepository(
    BaseRepositoryGet[UserDtoGetResponse, UserOrm],
    BaseRepositorySave[UserDtoGetResponse, UserDtoPostRequest, UserOrm],
    BaseRepositoryUpdate[UserDtoGetResponse, UserDtoPostRequest, UserOrm],
    BaseRepositoryDelete[UserDtoGetResponse, UserOrm]
):
    """Репозиторий для работы с данными пользователей"""
    model: type[UserOrm] = UserOrm
    dto_response: type[UserDtoGetResponse] = UserDtoGetResponse

    def get_by_email(self, email: str) -> UserDtoGetResponse:
        """Получение пользователя по email"""
        stmt = select(self.model).where(self.model.email == email)
        user_info = self.session.execute(stmt).scalar_one()
        return self._get_dto(user_info)

    def save(self, dto_post_request: UserDtoPostRequest) -> UserDtoGetResponse:
        """Сохранения пользователя"""
        orm_object = self.model(**dto_post_request.model_dump())
        orm_object.password = dto_post_request.password.get_secret_value().encode()
        self.session.add(orm_object)
        self.session.flush()
        return self._get_dto(orm_object)

    def get_hash_psw(self, user_id: str) -> bytes:
        """Получение хеша пароля"""
        stmt = select(self.model.password).where(self.model.id == user_id)
        password = self.session.execute(stmt).scalar_one_or_none()
        if not password:
            raise RecordNotFound(user_id)
        return password