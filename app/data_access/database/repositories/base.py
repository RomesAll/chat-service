from datetime import datetime, timezone
from typing import Generic
from uuid import UUID
from app.data_access.database.models.base import BaseOrm
from sqlalchemy import select, between, and_, or_, delete, Select
from sqlalchemy.orm import Session
from app.data_access.exceptions import RecordNotFound
from interfaces.repository import IRepository, TDtoId, TDtoGetResponse, TDtoPostPutDeleteRequest
from repositories.exception_handler import HandleSqlAlchemyException
from app.shared.dtos.base import (
    BaseDtoGetListRequest,
    SortEnum,
    OperatorEnum,
    BaseDtoOrmRecordGetResponse,
)

OPERATOR_MAP = {
    OperatorEnum.EQ: lambda f, v: f == v,
    OperatorEnum.NE: lambda f, v: f != v,
    OperatorEnum.GT: lambda f, v: f > v,
    OperatorEnum.GTE: lambda f, v: f >= v,
    OperatorEnum.LT: lambda f, v: f < v,
    OperatorEnum.LTE: lambda f, v: f <= v,
    OperatorEnum.LIKE: lambda f, v: f.like(f"%{v}%"),
    OperatorEnum.IN: lambda f, v: f.in_(v),
    OperatorEnum.BETWEEN: lambda f, v: between(f, v[0], v[1])
}


@HandleSqlAlchemyException()
class BaseRepository(
    Generic[TDtoId, TDtoGetResponse, TDtoPostPutDeleteRequest],
    IRepository[TDtoId, TDtoGetResponse, TDtoPostPutDeleteRequest]
):
    """Базовый репозиторий для работы с данными"""

    def __init__(
            self,
            session: Session
    ):
        self.dto_response: type[TDtoGetResponse] = BaseDtoOrmRecordGetResponse
        self.model: type[BaseOrm] = BaseOrm
        self.session: Session = session

    def get(self, dto_get_request: BaseDtoGetListRequest) -> list[TDtoGetResponse]:
        """Получение записи из бд"""
        pagination = dto_get_request.pagination
        limit, offset = pagination.limit, pagination.offset
        include_deleted = dto_get_request.include_deleted
        stmt: Select = (
            select(self.model).
            limit(limit).
            offset(offset)
        )
        stmt = self._accept_orders(stmt, dto_get_request)
        stmt = self._accept_filters(stmt, dto_get_request)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted == include_deleted)
        orm_objects = self.session.execute(stmt).scalars().all()
        dtos_response = [self.dto_response(**orm_object.to_dict()) for orm_object in orm_objects]
        return dtos_response

    def get_by_id(self, dto_record_id: TDtoId) -> TDtoGetResponse:
        """Получение записи по id"""
        orm_object = self._find_orm_object(dto_record_id)
        dto_response: BaseDtoOrmRecordGetResponse = self.dto_response(**orm_object.to_dict())
        return dto_response

    def save(self, dto_post_request: TDtoPostPutDeleteRequest) -> TDtoGetResponse | None:
        """Сохранение записи в бд"""
        orm_object = self.model(**dto_post_request.model_dump())
        self.session.add(orm_object)
        self.session.flush()
        return self._get_dto_or_none(dto_post_request, orm_object)

    def update(self, dto_update_request: TDtoPostPutDeleteRequest) -> TDtoGetResponse | None:
        """Обновление записи в бд"""
        orm_object = self._find_orm_object(dto_update_request)
        raw_data: dict = dto_update_request.model_dump(exclude_unset=True)
        for field, value in raw_data.items():
            setattr(orm_object, field, value)
        self.session.flush()
        return self._get_dto_or_none(dto_update_request, orm_object)

    def soft_delete(self, dto_delete_request: TDtoPostPutDeleteRequest) -> TDtoGetResponse | bool | None:
        """Мягкое удаление из бд (с возможностью восстановления)"""
        orm_object = self._find_orm_object(dto_delete_request)
        result: bool = orm_object.soft_delete()
        return_object = self._get_dto_or_none(dto_delete_request, orm_object)
        return return_object if return_object else result

    def hard_delete(self, dto_delete_request: TDtoPostPutDeleteRequest) -> TDtoGetResponse | bool | None:
        """Удаление из бд"""
        stmt = delete(self.model).where(self.model.id == dto_delete_request.id).returning(self.model)
        result = self.session.execute(stmt)
        return_object = None
        if dto_delete_request.return_record:
            deleted_models: BaseOrm | None = result.scalars().first()
            if deleted_models:
                return_object = self._get_dto_or_none(dto_delete_request, deleted_models)
        return return_object if return_object else None

    def recovery(self, dto_delete_request: TDtoPostPutDeleteRequest) -> TDtoGetResponse | bool | None:
        """Восстановление удаленной записи"""
        orm_object = self._find_orm_object(dto_delete_request)
        result: bool = orm_object.soft_recovery()
        return_object = self._get_dto_or_none(dto_delete_request, orm_object)
        return return_object if return_object else result

    def _find_orm_object(self, orm_object_id: UUID) -> BaseOrm:
        """Поиск записи в бд по id"""
        stmt = select(self.model).where(
            self.model.id == orm_object_id
        )
        orm_object: BaseOrm | None = self.session.execute(stmt).scalar_one_or_none()
        if not orm_object:
            raise RecordNotFound(orm_object_id)
        return orm_object

    def _get_dto_or_none(self, dto_request: TDtoPostPutDeleteRequest, orm_object: BaseOrm) -> TDtoGetResponse | None:
        """Получение dto модели для ответа или none"""
        if dto_request.return_record:
            dto_response = self.dto_response(**orm_object.to_dict())
            dto_response.deleted_at = datetime.now(tz=timezone.utc)
            return dto_response
        return None

    def _accept_filters(self, stmt, dto_get_request: BaseDtoGetListRequest) -> Select:
        """Добавление фильтров к запросу"""
        filters = []
        for current_filter in dto_get_request.filters:
            field = getattr(self.model, current_filter.field)
            operator = current_filter.operator
            value = current_filter.value
            filters.append(OPERATOR_MAP.get(operator)(field, value))
        if dto_get_request.filters_logic == 'AND' and filters:
            stmt = stmt.where(and_(*filters))
        elif dto_get_request.filters_logic == 'OR' and filters:
            stmt = stmt.where(or_(*filters))
        return stmt

    def _accept_orders(self, stmt, dto_get_request: BaseDtoGetListRequest) -> Select:
        """Добавление сортировок к запросу"""
        orders = []
        for order in dto_get_request.sort:
            orm_field = getattr(self.model, order.field)
            if order.order_mode == SortEnum.DESC:
                orders.append(orm_field.desc())
            elif order.order_mode == SortEnum.ASC:
                orders.append(orm_field.asc())
        if orders:
            stmt = stmt.order_by(*orders)
        return stmt