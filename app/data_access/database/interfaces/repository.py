from abc import ABC, abstractmethod
from typing import Generic
from typing_extensions import TypeVar
from app.shared.dtos.base import (
    BaseDtoOrmRecordPostRequest,
    BaseDtoOrmRecordGetResponse,
    BaseDtoOrmRecord,
    BaseDtoGetListRequest
)

TDtoId = TypeVar('TDtoId', bound=BaseDtoOrmRecord)
TDtoGetResponse = TypeVar('TDtoGetResponse', bound=BaseDtoOrmRecordGetResponse)
TDtoPostPutDeleteRequest = TypeVar('TDtoPostPutDeleteRequest', bound=BaseDtoOrmRecordPostRequest)


class IRepository(Generic[TDtoId, TDtoGetResponse, TDtoPostPutDeleteRequest], ABC):
    """Класс интерфейса репозитория для доступа к данным"""

    @abstractmethod
    def get(
            self,
            dto_get_request: BaseDtoGetListRequest
    ) -> list[TDtoGetResponse]:
        """
        Метод получения списка записей
        :param dto_get_request: принимает dto объект BaseDtoGetRequest
        :return:
        """
        pass

    @abstractmethod
    def get_by_id(
            self,
            dto_record_id: TDtoId
    ) -> TDtoGetResponse:
        """
        Метод получения записей по id
        :param dto_record_id: принимает dto объект DtoGetByIdRequest
        :return:
        """
        pass

    @abstractmethod
    def save(
            self,
            dto_post_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse | None:
        """
        Сохранение записи
        :param dto_post_request: принимает объект BaseDtoPostRequest
        :return: возвращает либо None (если мы в dto указали return_value=False), либо созданные объект
        """
        pass

    @abstractmethod
    def update(
            self,
            dto_update_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse | None:
        """
        Обновление записи
        :param dto_update_request: принимает объект BaseDtoUpdateRequest
        :return: возвращает либо None (если мы в dto указали return_value=False), либо обновленный объект
        """
        pass

    @abstractmethod
    def hard_delete(
            self,
            dto_delete_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse | None:
        """
        Удаление записи из бд без возможности восстановления
        :param dto_delete_request: принимает объект BaseDtoDeleteRequest
        :return: возвращает либо None (если мы в dto указали return_value=False), либо удаленный объект
        """
        pass

    @abstractmethod
    def soft_delete(
            self,
            dto_delete_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse | None:
        """
        Мягкое удаление записи с возможностью восстановления
        :param dto_delete_request: принимает объект BaseDtoDeleteRequest
        :return: возвращает либо None (если мы в dto указали return_value=False), либо удаленный объект
        """
        pass

    @abstractmethod
    def recovery(
            self,
            dto_delete_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse | None:
        """
        Восстановление записи
        :param dto_delete_request: принимает объект BaseDtoDeleteRequest
        :return: возвращает либо None (если мы в dto указали return_value=False), либо удаленный объект
        """
        pass