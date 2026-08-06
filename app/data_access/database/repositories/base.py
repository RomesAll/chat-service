from datetime import datetime, timezone
from app.data_access.database.models.base import BaseOrm
from sqlalchemy import select, between, and_, or_, delete
from sqlalchemy.orm import Session
from exceptions import RecordNotFound
from interfaces.repository import IRepository
from repositories.exception_handler import HandleSqlAlchemyException
from app.shared.dtos.base import (
    BaseDtoGetResponse,
    DtoIdRecordRequest,
    BaseDtoGetListRequest, SortEnum, OperatorEnum, BaseDtoPostRequest, BaseDtoUpdateRequest, BaseDtoDeleteRequest
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
class BaseRepository(IRepository):
    """Базовый репозиторий для работы с данными"""
    def __init__(
            self,
            dto_response: type[BaseDtoGetResponse],
            model: type[BaseOrm],
            session: Session
    ):
        self.dto_response = dto_response
        self.model = model
        self.session: Session = session

    def get(self, dto_get_request: BaseDtoGetListRequest) -> list[BaseDtoGetResponse]:
        """Получение записи из бд"""
        pagination = dto_get_request.pagination
        limit, offset = pagination.limit, pagination.offset
        include_deleted = dto_get_request.include_deleted
        stmt = (
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

    def _accept_filters(self, stmt, dto_get_request):
        """Добавление фильтров к запросу"""
        filters = []
        for filter in dto_get_request.filters:
            field = getattr(self.model, filter.field)
            operator = filter.operator
            value = filter.value
            filters.append(OPERATOR_MAP.get(operator)(field, value))
        if dto_get_request.filters_logic == 'AND' and filters:
            stmt = stmt.where(and_(*filters))
        elif dto_get_request.filters_logic == 'OR' and filters:
            stmt = stmt.where(or_(*filters))
        return stmt

    def _accept_orders(self, stmt, dto_get_request):
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

    def get_by_id(self, dto_record_id: DtoIdRecordRequest) -> BaseDtoGetResponse:
        """Получение записи по id"""
        orm_object = self._find_orm_object(dto_record_id)
        dto_response: BaseDtoGetResponse = self.dto_response(**orm_object.to_dict())
        return dto_response

    def save(self, dto_post_request: BaseDtoPostRequest) -> BaseDtoGetResponse | None:
        """Сохранение записи в бд"""
        orm_object = self.model(**dto_post_request.model_dump())
        self.session.add(orm_object)
        self.session.flush()
        return self._get_dto_or_none(dto_post_request, orm_object)

    def update(self, dto_update_request: BaseDtoUpdateRequest) -> BaseDtoGetResponse | None:
        """Обновление записи в бд"""
        orm_object = self._find_orm_object(dto_update_request)
        raw_data: dict = dto_update_request.model_dump(exclude_unset=True)
        for field, value in raw_data.items():
            setattr(orm_object, field, value)
        self.session.flush()
        return self._get_dto_or_none(dto_update_request, orm_object)

    def soft_delete(self, dto_delete_request: BaseDtoDeleteRequest) -> BaseDtoGetResponse | bool | None:
        """Мягкое удаление из бд (с возможностью восстановления)"""
        orm_object = self._find_orm_object(dto_delete_request)
        result: bool = orm_object.soft_delete()
        return_object = self._get_dto_or_none(dto_delete_request, orm_object)
        return return_object if return_object else result

    def hard_delete(self, dto_delete_request: BaseDtoDeleteRequest) -> BaseDtoGetResponse | bool | None:
        """Удаление из бд"""
        stmt = delete(self.model).where(self.model.id == dto_delete_request.id).returning(self.model)
        result = self.session.execute(stmt)
        return_object = None
        if dto_delete_request.return_record:
            deleted_models: BaseOrm | None = result.scalars().first()
            if deleted_models:
                return_object = self._get_dto_or_none(dto_delete_request, deleted_models)
        return return_object if return_object else None

    def recovery(self, dto_delete_request: BaseDtoDeleteRequest) -> BaseDtoGetResponse | bool | None:
        """Восстановление удаленной записи"""
        orm_object = self._find_orm_object(dto_delete_request)
        result: bool = orm_object.soft_recovery()
        return_object = self._get_dto_or_none(dto_delete_request, orm_object)
        return return_object if return_object else result

    def _find_orm_object(self, dto_request: DtoIdRecordRequest) -> BaseOrm:
        """Поиск записи в бд по id"""
        stmt = select(self.model).where(
            self.model.id == dto_request.id
        )
        orm_object: BaseOrm | None = self.session.execute(stmt).scalar_one_or_none()
        if not orm_object:
            raise RecordNotFound(dto_request.id)
        return orm_object

    def _get_dto_or_none(self, dto: BaseDtoPostRequest, orm_object: BaseOrm) -> BaseDtoGetResponse | None:
        """Получение dto модели для ответа или none"""
        if dto.return_record:
            dto_response = self.dto_response(**orm_object.to_dict())
            dto_response.deleted_at = datetime.now(tz=timezone.utc)
            return dto_response
        return None