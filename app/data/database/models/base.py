from datetime import datetime
from enum import Enum
from typing import Iterable, Any
from uuid import UUID
from sqlalchemy import UUID as PUUID, inspect
from sqlalchemy import DateTime, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DynamicFields:
    """Подсказка для idea, чтобы он не подчеркивал поле Fields в orm моделях"""
    def __getattr__(self, name: str) -> str: ...
    def __iter__(self) -> Iterable[Any]: ...


class OrmFieldInfoMeta(type(DeclarativeBase)):
    """
    Метакласс для динамического создания enum с полями orm моделей.
    В объектах моделей будет динамически создаваться атрибут Fields.
    Они будут содержать список полей модели, которые могут пригодиться, например,
    для метода to_dict в параметре exclude, чтобы передать туда поля для исключения,

    например:
        user.to_dict(exclude=[UserOrm.Fields.ID])

    """
    def __init__(self, name, base, attrs):
        """Метод для перехвата создания объектов класса"""
        super().__init__(name, base, attrs)
        if hasattr(self, '__table__'):
            fields_dict = {
                field.description.upper(): field.description
                for field in list(self.__table__.columns)
            }
            enum_name = f'{name}Fields'
            enum = Enum(enum_name, fields_dict, type=str)
            self.Fields: DynamicFields = enum


class IdMixin:
    """Миксин для id"""
    id: Mapped[UUID] = mapped_column(PUUID, primary_key=True, unique=True)


class TimeStampMixin:
    """Миксин для временных меток"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
        server_onupdate=text("TIMEZONE('UTC', now())"),
        nullable=False
    )


class BaseOrm(DeclarativeBase, metaclass=OrmFieldInfoMeta):
    """Базовый абстрактный класс для orm моделей"""
    __abstract__ = True
    Fields: DynamicFields
    is_deleted: Mapped[bool] = mapped_column(default=False)

    def to_dict(
            self,
            exclude: Iterable[str] | None = None,
            uuid_is_str: bool = False
    ) -> dict:
        """
        Метод для сериализации данных orm моделей
        :param exclude: поля, которые нужно исключить принимает объекты BaseOrm.Fields.<название поля в верхнем регистре>
        :param uuid_is_str: нужно ли преобразовывать uuid в строку
        :return: dict
        """
        serializers_data = {}
        for field in inspect(self.__class__).columns:
            if not field.name.startswith('_'):
                data = getattr(self, field.name)
                if isinstance(data, UUID) and uuid_is_str:
                    data = str(data)
                serializers_data.update({
                    field.name: data
                })

        if not exclude:
            return serializers_data
        exclude_data = {field for field in exclude}
        return {
            field : value
            for field, value in serializers_data.items()
            if field not in exclude_data
        }

    def soft_delete(self) -> bool:
        """Мягкое удаление"""
        self.is_deleted = True
        return bool(self.is_deleted)

    def soft_recovery(self) -> bool:
        """Мягкое восстановление"""
        self.is_deleted = False
        return bool(self.is_deleted)