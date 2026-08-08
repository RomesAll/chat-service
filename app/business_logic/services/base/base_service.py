from typing import Generic
from business_logic.unit_of_work import UnitOfWork
from interfaces.repository import TDtoId, TDtoGetResponse, TDtoPostPutDeleteRequest
from repositories.base import BaseRepository
from shared.dtos.base import BaseDtoGetListRequest


class BaseService(
    Generic[TDtoId, TDtoGetResponse, TDtoPostPutDeleteRequest]
):
    def __init__(
            self,
            repository: type[BaseRepository]
    ):
        self.repository = repository

    def get(
            self,
            uow: UnitOfWork,
            dto_get_request: BaseDtoGetListRequest
    ) -> list[TDtoGetResponse]:
        """Получение записи из бд"""
        results: list[TDtoGetResponse] = uow.get_repository(self.repository).get(dto_get_request)
        return results

    def get_by_id(
            self,
            uow: UnitOfWork,
            dto_record_id: TDtoId
    ) -> TDtoGetResponse:
        """Получение записи по id"""
        result: TDtoGetResponse = uow.get_repository(self.repository).get_by_id(dto_record_id)
        return result

    def save(
            self,
            uow: UnitOfWork,
            dto_post_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse | None:
        """Сохранение записи в бд"""
        result: TDtoGetResponse | None = uow.get_repository(self.repository).save(dto_post_request)
        return result

    def update(
            self,
            uow: UnitOfWork,
            dto_update_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse | None:
        """Обновление записи в бд"""
        result: TDtoGetResponse | None = uow.get_repository(self.repository).update(dto_update_request)
        return result

    def soft_delete(
            self,
            uow: UnitOfWork,
            dto_delete_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse | bool | None:
        """Мягкое удаление из бд (с возможностью восстановления)"""
        result: TDtoGetResponse | bool | None = uow.get_repository(self.repository).soft_delete(dto_delete_request)
        return result

    def hard_delete(
            self,
            uow: UnitOfWork,
            dto_delete_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse | bool | None:
        """Удаление из бд"""
        result: TDtoGetResponse | bool | None = uow.get_repository(self.repository).hard_delete(dto_delete_request)
        return result

    def recovery(
            self,
            uow: UnitOfWork,
            dto_delete_request: TDtoPostPutDeleteRequest
    ) -> TDtoGetResponse | bool | None:
        """Восстановление удаленной записи"""
        result: TDtoGetResponse | bool | None = uow.get_repository(self.repository).recovery(dto_delete_request)
        return result
