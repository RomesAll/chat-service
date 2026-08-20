from .exception_handler import HandleSqlAlchemyException
from abc import ABCMeta


class ExceptionHandlingMeta(ABCMeta):
    """Метакласс для декорирования репозиториев"""
    def __next__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        handler = HandleSqlAlchemyException()
        return handler(new_class)
