from enum import Enum
from typing import Iterable, Any

from sqlalchemy.orm import DeclarativeBase

class DynamicFields:
    def __getattr__(self, name: str) -> str: ...
    def __iter__(self) -> Iterable[Any]: ...

class OrmFieldInfoMeta(type(DeclarativeBase)):
    def __init__(self, name, base, attrs):
        super().__init__(name, base, attrs)
        if hasattr(self, '__table__'):
            fields_dict = {
                field.description.upper(): field.description
                for field in list(self.__table__.columns)
            }
            enum_name = f'{name}Fields'
            enum = Enum(enum_name, fields_dict, type=str)
            self.Fields: DynamicFields = enum

class BaseOrm(DeclarativeBase, metaclass=OrmFieldInfoMeta):
    __abstract__ = True
    Fields: DynamicFields