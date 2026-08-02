from enum import Enum
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator


class OperatorEnum(str, Enum):
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
    ASC = 'asc'
    DESC = 'desc'


class PaginationDto(BaseModel):
    limit: int = Field(20, ge=1, le=500, description='Количество записей')
    offset: int = Field(0, ge=0, description='Смещение')


class FilterDto(BaseModel):
    field: str = Field(..., description='Название колонки (поля)')
    operator: OperatorEnum = Field(OperatorEnum.EQ, description='Оператор сравнения')
    value: Any = Field(..., description='Значение для фильтрации')

    @model_validator(mode='after')
    def validate(self):
        value = self.value
        if self.operator.BETWEEN and (type(value) not in [list, tuple] and len(value) != 2):
            raise ValueError('При выборе оператора BETWEEN для фильтрации '
                             'записей два значения нужно поместить в '
                             f'коллекцию list, tuple, передан объект {type(value)}')
        return self

class FiltersDto(BaseModel):
    filters: list[FilterDto] = Field(default_factory=list)
    logic: str = Field('AND', description='Логическая операция AND или OR')


class SortDto(BaseModel):
    field: str = Field(..., description='Название колонки (поля)')
    order: SortEnum = Field(SortEnum.ASC, description="Порядок сортировки")

