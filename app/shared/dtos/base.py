from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, model_validator, field_validator, ConfigDict


class OperatorEnum(str, Enum):
    """Список условий"""
    EQ = 'eq'
    NE = 'ne'
    GT = 'gt'
    GTE = 'gte'
    LT = 'lt'
    LTE = 'lte'
    LIKE = 'like'
    ILIKE = 'ilike'
    IN = 'in'
    BETWEEN = 'between'


class SortEnum(str, Enum):
    """Режимы сортировок"""
    ASC = 'asc'
    DESC = 'desc'


class PaginationDto(BaseModel):
    """Пагинация для записей"""
    limit: int = Field(20, ge=1, le=500, description='Количество записей', )
    offset: int = Field(0, ge=0, description='Смещение')


class FilterDto(BaseModel):
    """Правила фильтрации записей"""
    field: str = Field(..., description='Название колонки (поля)')
    operator: OperatorEnum = Field(OperatorEnum.EQ, description='Оператор сравнения')
    value: Any = Field(..., description='Значение для фильтрации')

    @model_validator(mode='after')
    def validate(self):
        value = self.value
        if self.operator == self.operator.BETWEEN and (type(value) not in [list, tuple] and len(value) != 2):
            raise ValueError('При выборе оператора BETWEEN для фильтрации '
                             'записей два значения нужно поместить в '
                             f'коллекцию list, tuple, передан объект {type(value)}')

        if self.operator == OperatorEnum.IN:
            if not isinstance(self.value, list):
                raise ValueError('IN требует список')

        return self


class SortDto(BaseModel):
    """Хранения данных для сортировки"""
    field: str = Field(..., description='Название колонки (поля)')
    order_mode: SortEnum = Field(SortEnum.ASC, description="Порядок сортировки")


class BaseDtoGetListRequest(BaseModel):
    """Базовый класс для получения списка записей с пагинацией, фильтрами и сортировкой"""
    pagination: PaginationDto = Field(..., description='Пагинация для записей')
    filters: list[FilterDto] = Field(default_factory=list, description='Фильтрация для записей')
    filters_logic: str = Field('AND', description='Логическая операция AND или OR (с предыдущем фильтров')
    sort: list[SortDto] = Field(default_factory=list, description='Сортировка для записей')
    include_deleted: bool = Field(False, description='Включить удаленные объекты?')

    @model_validator(mode='after')
    def validate(self):
        if self.filters_logic.upper() not in ['AND', 'OR']:
            raise ValueError('logic должен быть AND или OR')
        return self


class DtoIdRecordRequest(BaseModel):
    """Dto модель для хранения id записей"""
    id: UUID | int | str = Field(..., description='Идентификатор записи в бд')


class BaseDtoPostRequest(DtoIdRecordRequest):
    """Базовый класс dto модели для хранения данных предназначенных для сохранения"""
    return_record: bool = Field(False, exclude=True)


class BaseDtoUpdateRequest(BaseDtoPostRequest):
    """Базовый класс dto модели для хранения данных предназначенных для обновления"""
    id: UUID | int | str = Field(..., exclude=True, description='Идентификатор записи в бд')


class BaseDtoDeleteRequest(BaseDtoPostRequest):
    """Базовый класс dto модели для хранения данных предназначенных для удаления"""
    pass


class BaseDtoGetResponse(DtoIdRecordRequest):
    """Базовый класс dto модели для хранения полученной информации"""
    created_at: datetime
    updated_at: datetime
    datetime_get: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description='Время получения записей'
    )
    is_deleted: bool = False
    model_config = ConfigDict(extra='allow')

    @field_validator('created_at', 'updated_at')
    def validate_utc_time(cls, value):
        if isinstance(value, datetime):
            if value.tzinfo != timezone.utc:
                value = value.replace(tzinfo=timezone.utc)
        return value