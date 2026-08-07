from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, model_validator, field_validator, ConfigDict


class OperatorEnum(str, Enum):
    """Перечисление вариантов условий для фильтрации"""
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
    """Перечисление вариантов сортировок"""
    ASC = 'asc'
    DESC = 'desc'


class PaginationDto(BaseModel):
    """DTO для хранения правил пагинаций объектов"""
    limit: int = Field(20, ge=1, le=500, description='Количество записей', )
    offset: int = Field(0, ge=0, description='Смещение')


class FilterDto(BaseModel):
    """DTO для хранения правил фильтрации объектов"""
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
    """DTO для хранения настройки сортировок"""
    field: str = Field(..., description='Название колонки (поля)')
    order_mode: SortEnum = Field(SortEnum.ASC, description="Порядок сортировки")


class BaseDtoGetListRequest(BaseModel):
    """
    Базовый DTO для операции получения списка объектов по
    определенным фильтрам, сортировкам и с учетом пагинации
    и неактивных объектов
    """
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


class BaseModelWithPrint(BaseModel):
    """
    Базовый DTO для красивого вывода в консоль моделей
    """
    def __str__(self):
        result = f'\n|------|{self.__class__.__name__}|------|'
        result += self.print() + '\n'
        return result

    def print(self, level: int = 0, max_level = 2):
        fields = list(self.__class__.model_fields.keys())
        delimiter_indent = len(max(fields, key=len)) + 1
        result = '\n' if level == 0 else ''
        if level >= max_level:
            return f'{'      ' * level}[{self.__class__.__name__}]: {self}\n'
        for ind, field in enumerate(fields, start=0):
            value = getattr(self, field)
            current_row_indent = delimiter_indent - len(field)
            if type(value) in [list, tuple, set]:
                result += f'{'      ' * level}[{field.upper()}]{' ' * current_row_indent}:\n'
                for wrap_ind, wrap_value in enumerate(value, start=0):
                    if isinstance(wrap_value, BaseModelWithPrint):
                        result += wrap_value.print(level + 1) + '\n\n'
                    else:
                        result += f'{'      ' * (level + 1)}[{wrap_value.__class__.__name__}]{' ' * current_row_indent}: {value}\n'
            else:
                result += f'{'      ' * level}[{field.upper()}]{' ' * current_row_indent}: {value}'
                if ind < len(fields) - 1:
                    result += '\n'
        return result


class BaseDtoOrmRecord(BaseModelWithPrint):
    """Базовый DTO с общими полями для всех операций"""
    id: UUID


class BaseDtoOrmRecordGetResponse(BaseDtoOrmRecord):
    """Базовый DTO с общими полями для операции получения (Get)"""
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


class BaseDtoOrmRecordPostRequest(BaseDtoOrmRecord):
    """Базовый DTO с общими полями для операции добавления (Post)"""
    return_record: bool = Field(False, exclude=True)


class BaseDtoOrmRecordPutResponse(BaseDtoOrmRecordPostRequest):
    """Базовый DTO с общими полями для операции обновления (Put)"""
    id: UUID = Field(..., exclude=True)


class BaseDtoOrmRecordDeleteResponse(BaseDtoOrmRecordPostRequest):
    """Базовый DTO с общими полями для операции удаления (Delete)"""
    pass
