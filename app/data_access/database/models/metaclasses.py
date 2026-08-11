from enum import Enum
from typing import Iterable, Any, Type, cast
from sqlalchemy import Table
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from app.data_access.exceptions import (
    ValidationOrmNotDocError,
    ValidationOrmIncorrectDocError,
    ValidationOrmNotTableNameError,
    ValidationOrmIncorrectTableNameError
)


class DynamicFields:
    """Подсказка для idea, чтобы он не подчеркивал поле Fields в orm моделях"""
    def __getattr__(self, name: str) -> str: ...
    def __iter__(self) -> Iterable[Any]: ...


class SqlAlchemyOrmBaseMeta(type(DeclarativeBase)):
    pass


class RegistryMeta(SqlAlchemyOrmBaseMeta):
    """Метакласс для автоматической регистрации всех моделей."""
    _registry = {}

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if not attrs.get('__abstract__', False) and '__tablename__' in attrs:
            if RegistryMeta._registry.get(name.lower()) is None:
                RegistryMeta._registry[name.lower()] = new_class
                print(f"Модель зарегистрирована: {name}")
        return new_class

    @classmethod
    def get_all_models(cls):
        return list(cls._registry.values())


class AutoCreateTable(RegistryMeta):
    """
    Метакласс для автоматического создания таблиц в базе данных
    с проверкой существования
    """
    __engine = None

    @classmethod
    def set_engine(cls, engine):
        """Метод для установки engine"""
        cls.__engine = engine

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if not issubclass(new_class, DeclarativeBase):
            raise TypeError(f"{new_class} класс должен быть подклассом DeclarativeBase")
        class_obj: Type[DeclarativeBase] = new_class
        try:
            if cls.__engine and '__tablename__' in attrs:
                table = cast(Table, class_obj.__table__)
                table.create(cls.__engine, checkfirst=True)
        except SQLAlchemyError as e:
            raise 
        return new_class


class ValidationOrmMeta(AutoCreateTable):
    """
    Метакласс для валидации orm моделей, с проверкой обязательной
    документации к коду и названием таблицы
    """
    def __new__(cls, name, bases, attrs):
        name_model = attrs.get('__qualname__')

        if '__doc__' not in attrs:
            raise ValidationOrmNotDocError(name_model)

        doc_len = len(attrs['__doc__'])
        if doc_len < ValidationOrmIncorrectDocError.MIN_COUNT_CHAR:
            raise ValidationOrmIncorrectDocError(name_model, doc_len)

        if attrs.get('__abstract__', None):
            return super().__new__(cls, name, bases, attrs)

        if '__tablename__' not in attrs:
            raise ValidationOrmNotTableNameError(name_model)

        table_len = len(attrs['__tablename__'])
        if table_len < ValidationOrmIncorrectTableNameError.MIN_COUNT_CHAR:
            raise ValidationOrmIncorrectTableNameError(name_model, table_len)

        return super().__new__(cls, name, bases, attrs)


class OrmFieldInfoMeta(ValidationOrmMeta):
    """
    Метакласс для динамического создания enum с полями orm моделей.
    В объектах моделей будет динамически создаваться атрибут Fields.
    Они будут содержать список полей модели, которые могут пригодиться, например,
    для метода to_dict в параметре exclude, чтобы передать туда поля для исключения,

    например:
        user.to_dict(exclude=[UserOrm.Fields.ID])

    """
    def __init__(self, name, bases, attrs):
        """Метод для перехвата создания объектов класса"""
        super().__init__(name, bases, attrs)
        if hasattr(self, '__table__'):
            fields_dict = {
                field.description.upper(): field.description
                for field in list(self.__table__.columns)
            }
            enum_name = f'{name}Fields'
            enum = Enum(enum_name, fields_dict, type=str)
            self.Fields: DynamicFields = enum


class OrmManagerMeta(OrmFieldInfoMeta):
    @classmethod
    def get_all_models(cls):
        return list(cls._registry.values())