from typing import cast
from sqlalchemy.orm import Session
from app.shared.dtos.message import PrivateMessageDtoGetResponse, GroupMessageDtoGetResponse
from models.message import PrivateMessageOrm, GroupMessageOrm
from shared.dtos.base import BaseDtoGetListRequest, DtoIdRecordRequest
from .base import BaseRepository
from shared.dtos.message import (
    PrivateMessageDtoPostRequest,
    MessageDtoUpdateRequest,
    MessageDtoDeleteRequest,
    GroupMessageDtoPostRequest
)


class PrivateMessageRepository(BaseRepository):
    """Репозиторий для работы с данными приватных сообщений"""
    def __init__(self, session: Session):
        super().__init__(
            dto_response=PrivateMessageDtoGetResponse,
            session=session,
            model=PrivateMessageOrm
        )

    def get(self, dto_get_request: BaseDtoGetListRequest) -> list[PrivateMessageDtoGetResponse]:
        """
        Получение списка приватных сообщений
        :param dto_get_request:
        :return:
        """
        return cast(list[PrivateMessageDtoGetResponse], super().get(dto_get_request))

    def get_by_id(self, dto_record_id: DtoIdRecordRequest) -> PrivateMessageDtoGetResponse:
        """
        Получение приватного сообщения по id
        :param dto_record_id:
        :return:
        """
        return cast(PrivateMessageDtoGetResponse, super().get_by_id(dto_record_id))

    def save(self, dto_post_request: PrivateMessageDtoPostRequest) -> PrivateMessageDtoGetResponse | None:
        """
        Сохранение приватного сообщения
        :param dto_post_request:
        :return:
        """
        result = super().save(dto_post_request)
        if result:
            return cast(PrivateMessageDtoGetResponse, result)
        return None

    def update(self, dto_update_request: MessageDtoUpdateRequest) -> PrivateMessageDtoGetResponse | None:
        """
        Обновление данных приватных сообщений
        :param dto_update_request:
        :return:
        """
        result = super().update(dto_update_request)
        if result:
            return cast(PrivateMessageDtoGetResponse, result)
        return None

    def soft_delete(self, dto_delete_request: MessageDtoDeleteRequest) -> PrivateMessageDtoGetResponse | bool | None:
        """
        Мягкое удаление приватного сообщения с возможностью восстановления
        :param dto_delete_request:
        :return:
        """
        result = super().soft_delete(dto_delete_request)
        if result:
            return cast(PrivateMessageDtoGetResponse, result)
        return None

    def hard_delete(self, dto_delete_request: MessageDtoDeleteRequest) -> PrivateMessageDtoGetResponse | bool | None:
        """
        Жесткое удаление приватного сообщения без возможности восстановления
        :param dto_delete_request:
        :return:
        """
        result = super().hard_delete(dto_delete_request)
        if result:
            return cast(PrivateMessageDtoGetResponse, result)
        return None

    def recovery(self, dto_delete_request: MessageDtoDeleteRequest) -> PrivateMessageDtoGetResponse | bool | None:
        """
        Восстановление приватного сообщения
        :param dto_delete_request:
        :return:
        """
        result = super().recovery(dto_delete_request)
        if result:
            return cast(PrivateMessageDtoGetResponse, result)
        return None


class GroupMessageRepository(BaseRepository):
    """Репозиторий для работы с данными групповых сообщений"""
    def __init__(self, session: Session):
        super().__init__(
            dto_response=GroupMessageDtoGetResponse,
            session=session,
            model=GroupMessageOrm
        )

    def get(self, dto_get_request: BaseDtoGetListRequest) -> list[GroupMessageDtoGetResponse]:
        """
        Получение списка групповых сообщений
        :param dto_get_request:
        :return:
        """
        return cast(list[GroupMessageDtoGetResponse], super().get(dto_get_request))

    def get_by_id(self, dto_record_id: DtoIdRecordRequest) -> GroupMessageDtoGetResponse:
        """
        Получение групповых сообщений по id
        :param dto_record_id:
        :return:
        """
        return cast(GroupMessageDtoGetResponse, super().get_by_id(dto_record_id))

    def save(self, dto_post_request: GroupMessageDtoPostRequest) -> GroupMessageDtoGetResponse | None:
        """
        Сохранение сообщений
        :param dto_post_request:
        :return:
        """
        result = super().save(dto_post_request)
        if result:
            return cast(GroupMessageDtoGetResponse, result)
        return None

    def update(self, dto_update_request: MessageDtoUpdateRequest) -> GroupMessageDtoGetResponse | None:
        """
        Обновление групповых сообщений
        :param dto_update_request:
        :return:
        """
        result = super().update(dto_update_request)
        if result:
            return cast(GroupMessageDtoGetResponse, result)
        return None

    def soft_delete(self, dto_delete_request: MessageDtoDeleteRequest) -> GroupMessageDtoGetResponse | bool | None:
        """
        Мягкое удаление групповых сообщений с возможностью восстановления
        :param dto_delete_request:
        :return:
        """
        result = super().soft_delete(dto_delete_request)
        if result:
            return cast(GroupMessageDtoGetResponse, result)
        return None

    def hard_delete(self, dto_delete_request: MessageDtoDeleteRequest) -> GroupMessageDtoGetResponse | bool | None:
        """
        Жесткое удаление групповых сообщений без возможности восстановления
        :param dto_delete_request:
        :return:
        """
        result = super().hard_delete(dto_delete_request)
        if result:
            return cast(GroupMessageDtoGetResponse, result)
        return None

    def recovery(self, dto_delete_request: MessageDtoDeleteRequest) -> GroupMessageDtoGetResponse | bool | None:
        """
        Восстановление групповых сообщений
        :param dto_delete_request:
        :return:
        """
        result = super().recovery(dto_delete_request)
        if result:
            return cast(GroupMessageDtoGetResponse, result)
        return None
