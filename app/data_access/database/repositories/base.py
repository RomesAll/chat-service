from typing import Generic
from uuid import UUID
from app.data_access.database.models.base import BaseOrm
from sqlalchemy import select, between, and_, or_, delete, Select, exists
from sqlalchemy.orm import Session
from app.data_access.exceptions import RecordNotFound
from dtos import BaseDtoGetResponse
from interfaces.repository import IRepository, TDtoId, TDtoGetResponse, TDtoPostPutDeleteRequest
from repositories.exception_handler import HandleSqlAlchemyException
from app.shared.dtos import (
    BaseDtoGetListRequest,
    SortEnum,
    OperatorEnum,
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
        self.dto_response: type[TDtoGetResponse] = BaseDtoGetResponse
        self.model: type[BaseOrm] = BaseOrm
        self.session: Session = session

    def check_exist(self, record_id: UUID | str | int) -> bool:
        """Проверка существования записи"""
        exists_query = select(
            exists().where(self.model.id == record_id)
        )
        exists_result: bool | None = self.session.execute(exists_query).scalar()
        if not exists_result:
            return False
        return exists_result

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

    def get_by_id(self, record_id: UUID | str | int) -> TDtoGetResponse:
        """Получение записи по id"""
        orm_object = self._find_orm_object(record_id)
        dto_response = self.dto_response(**orm_object.to_dict())
        return dto_response

    def save(self, dto_post_request: TDtoPostPutDeleteRequest) -> TDtoGetResponse:
        """Сохранение записи в бд"""
        orm_object = self.model(**dto_post_request.model_dump())
        self.session.add(orm_object)
        self.session.flush()
        return self._get_dto(orm_object)

    def update(self, dto_update_request: TDtoPostPutDeleteRequest) -> TDtoGetResponse:
        """Обновление записи в бд"""
        orm_object = self._find_orm_object(dto_update_request.id)
        raw_data: dict = dto_update_request.model_dump(exclude_unset=True, exclude_none=True, exclude_defaults=True)
        for field, value in raw_data.items():
            setattr(orm_object, field, value)
        self.session.flush()
        return self._get_dto(orm_object)

    def soft_delete(self, record_id: UUID | str | int) -> UUID | str | int:
        """Мягкое удаление из бд (с возможностью восстановления)"""
        orm_object = self._find_orm_object(record_id)
        orm_object.soft_delete()
        return record_id

    def hard_delete(self, record_id: UUID | str | int) -> UUID | str | int:
        """Удаление из бд"""
        stmt = delete(self.model).where(self.model.id == record_id)
        self.session.execute(stmt)
        return record_id

    def recovery(self, record_id: UUID | str | int) -> TDtoGetResponse:
        """Восстановление удаленной записи"""
        orm_object = self._find_orm_object(record_id)
        orm_object.soft_recovery()
        dto_response = self._get_dto(orm_object)
        return dto_response

    def _find_orm_object(self, orm_object_id: UUID | str | int) -> BaseOrm:
        """Поиск записи в бд по id"""
        stmt = select(self.model).where(
            self.model.id == orm_object_id
        )
        orm_object: BaseOrm | None = self.session.execute(stmt).scalar_one_or_none()
        if not orm_object:
            raise RecordNotFound(orm_object_id)
        return orm_object

    def _get_dto(self, orm_object: BaseOrm) -> TDtoGetResponse:
        """Получение dto модели для ответа или none"""
        dto_response = self.dto_response(**orm_object.to_dict())
        return dto_response

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