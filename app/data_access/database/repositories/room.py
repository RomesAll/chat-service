from typing import cast
from sqlalchemy.orm import Session
from app.shared.dtos.room import RoomDtoGetResponse
from models.room import RoomOrm
from shared.dtos.base import BaseDtoGetListRequest, DtoIdRecordRequest
from shared.dtos.room import RoomDtoPostRequest, RoomDtoUpdateRequest, RoomDtoDeleteRequest
from .base import BaseRepository


class RoomRepository(BaseRepository):
    """Репозиторий для работы с данными групп"""
    def __init__(self, session: Session):
        super().__init__(
            dto_response=RoomDtoGetResponse,
            session=session,
            model=RoomOrm
        )

    def get(self, dto_get_request: BaseDtoGetListRequest) -> list[RoomDtoGetResponse]:
        """
        Получение списка комнат
        :param dto_get_request:
        :return:
        """
        return cast(list[RoomDtoGetResponse], super().get(dto_get_request))

    def get_by_id(self, dto_record_id: DtoIdRecordRequest) -> RoomDtoGetResponse:
        """
        Получение комнат по id
        :param dto_record_id:
        :return:
        """
        return cast(RoomDtoGetResponse, super().get_by_id(dto_record_id))

    def save(self, dto_post_request: RoomDtoPostRequest) -> RoomDtoGetResponse | None:
        """
        Сохранение комнаты
        :param dto_post_request:
        :return:
        """
        result = super().save(dto_post_request)
        if result:
            return cast(RoomDtoGetResponse, result)
        return None

    def update(self, dto_update_request: RoomDtoUpdateRequest) -> RoomDtoGetResponse | None:
        """
        Обновление данных комнаты
        :param dto_update_request:
        :return:
        """
        result = super().update(dto_update_request)
        if result:
            return cast(RoomDtoGetResponse, result)
        return None

    def soft_delete(self, dto_delete_request: RoomDtoDeleteRequest) -> RoomDtoGetResponse | bool | None:
        """
        Мягкое удаление комнаты с возможностью восстановления
        :param dto_delete_request:
        :return:
        """
        result = super().soft_delete(dto_delete_request)
        if result:
            return cast(RoomDtoGetResponse, result)
        return None

    def hard_delete(self, dto_delete_request: RoomDtoDeleteRequest) -> RoomDtoGetResponse | bool | None:
        """
        Жесткое удаление комнаты без возможности восстановления
        :param dto_delete_request:
        :return:
        """
        result = super().hard_delete(dto_delete_request)
        if result:
            return cast(RoomDtoGetResponse, result)
        return None

    def recovery(self, dto_delete_request: RoomDtoDeleteRequest) -> RoomDtoGetResponse | bool | None:
        """
        Восстановление комнаты
        :param dto_delete_request:
        :return:
        """
        result = super().recovery(dto_delete_request)
        if result:
            return cast(RoomDtoGetResponse, result)
        return None