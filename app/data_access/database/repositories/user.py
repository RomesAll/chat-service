from typing import cast
from sqlalchemy.orm import Session
from app.shared.dtos.base import DtoIdRecordRequest
from app.shared.dtos.user import UserDtoGetResponse, UserDtoPostRequest, UserDtoUpdateRequest
from models.user import UserOrm
from shared.dtos.base import BaseDtoGetListRequest
from .base import BaseRepository


class UserRepository(BaseRepository):
    """Репозиторий для работы с данными пользователей"""
    def __init__(self, session: Session):
        super().__init__(
            dto_response=UserDtoGetResponse,
            session=session,
            model=UserOrm
        )

    def get(self, dto_get_request: BaseDtoGetListRequest) -> list[UserDtoGetResponse]:
        """
        Получение списка пользователей
        :param dto_get_request:
        :return:
        """
        return cast(list[UserDtoGetResponse], super().get(dto_get_request))

    def get_by_id(self, dto_record_id: DtoIdRecordRequest) -> UserDtoGetResponse:
        """
        Получение пользователей по id
        :param dto_record_id:
        :return:
        """
        return cast(UserDtoGetResponse, super().get_by_id(dto_record_id))

    def save(self, dto_post_request: UserDtoPostRequest) -> UserDtoGetResponse | None:
        """
        Сохранение пользователей
        :param dto_post_request:
        :return:
        """
        result = super().save(dto_post_request)
        if result:
            return cast(UserDtoGetResponse, result)
        return None

    def update(self, dto_update_request: UserDtoUpdateRequest) -> UserDtoGetResponse | None:
        """
        Обновление данных пользователя
        :param dto_update_request:
        :return:
        """
        result = super().update(dto_update_request)
        if result:
            return cast(UserDtoGetResponse, result)
        return None