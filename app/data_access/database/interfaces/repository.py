from abc import ABC, abstractmethod
from typing import Generic
from uuid import UUID

from typing_extensions import TypeVar
from app.shared.dtos import (
    BaseDtoClientRequest,
    BaseDtoGetResponse,
    BaseDtoGetListRequest
)

TDtoId = TypeVar('TDtoId', bound=BaseDtoClientRequest)
TDtoGetResponse = TypeVar('TDtoGetResponse', bound=BaseDtoGetResponse)
TDtoPostPutDeleteRequest = TypeVar('TDtoPostPutDeleteRequest', bound=BaseDtoClientRequest)


class IRepository(Generic[TDtoId, TDtoGetResponse, TDtoPostPutDeleteRequest], ABC):
    """Класс интерфейса репозитория для доступа к данным"""

    @abstractmethod
    def check_exist(
            self,
            dto_record_id: UUID | str | int
    ) -> bool:
        """
        Метод для проверки существования записи
        :param dto_record_id:
        :return:
        """
        pass

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
            record_id: UUID | str | int
    ) -> TDtoGetResponse:
        """
        Метод получения записей по id
        :param record_id
        :return:
        """
        pass

    @abstractmethod
    def save(
            self,
            dto_post_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse:
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
    ) -> TDtoGetResponse:
        """
        Обновление записи
        :param dto_update_request: принимает объект BaseDtoUpdateRequest
        :return: возвращает либо None (если мы в dto указали return_value=False), либо обновленный объект
        """
        pass

    @abstractmethod
    def hard_delete(
            self,
            record_id: UUID | str | int
    ) -> UUID | str | int:
        """
        Удаление записи из бд без возможности восстановления
        :param record_id:
        :return: возвращает либо None (если мы в dto указали return_value=False), либо удаленный объект
        """
        pass

    @abstractmethod
    def soft_delete(
            self,
            record_id: UUID | str | int
    ) -> UUID | str | int:
        """
        Мягкое удаление записи с возможностью восстановления
        :param record_id:
        :return: возвращает либо None (если мы в dto указали return_value=False), либо удаленный объект
        """
        pass

    @abstractmethod
    def recovery(
            self,
            record_id: UUID | str | int
    ) -> TDtoGetResponse:
        """
        Восстановление записи
        :param record_id:
        :return: возвращает либо None (если мы в dto указали return_value=False), либо удаленный объект
        """
        pass