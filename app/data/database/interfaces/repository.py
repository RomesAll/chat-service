from abc import ABC, abstractmethod
from app.services.dtos.base import (
    BaseDtoGetRequest,
    DtoGetByIdRequest,
    BaseDtoPostRequest,
    BaseDtoUpdateRequest,
    BaseDtoGetResponse, BaseDtoDeleteRequest
)


class IRepository(ABC):
    """Интерфейс репозитория для доступа к данным"""
    @abstractmethod
    def get(self, dto_get_request: BaseDtoGetRequest) -> BaseDtoGetResponse:
        """
        Метод получения списка записей
        :param dto_get_request: принимает dto объект BaseDtoGetRequest
        :return:
        """
        pass

    @abstractmethod
    def get_by_id(self, dto_record_id: DtoGetByIdRequest) -> BaseDtoGetResponse:
        """
        Метод получения записей по id
        :param dto_record_id: принимает dto объект DtoGetByIdRequest
        :return:
        """
        pass

    @abstractmethod
    def save(self, dto_post_request: BaseDtoPostRequest) -> BaseDtoGetResponse | None:
        """
        Сохранение записи
        :param dto_post_request: принимает объект BaseDtoPostRequest
        :return: возвращает либо None (если мы в dto указали return_value=False), либо созданные объект
        """
        pass

    @abstractmethod
    def update(self, dto_update_request: BaseDtoUpdateRequest) -> BaseDtoGetResponse | None:
        """
        Обновление записи
        :param dto_update_request: принимает объект BaseDtoUpdateRequest
        :return: возвращает либо None (если мы в dto указали return_value=False), либо обновленный объект
        """
        pass

    @abstractmethod
    def delete(self, dto_delete_request: BaseDtoDeleteRequest) -> BaseDtoGetResponse | None:
        """
        Удаление записи
        :param dto_delete_request: принимает объект BaseDtoDeleteRequest
        :return: возвращает либо None (если мы в dto указали return_value=False), либо удаленный объект
        """
        pass
