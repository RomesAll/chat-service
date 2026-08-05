from typing import TYPE_CHECKING, Callable
import psycopg.errors
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    InterfaceError,
    TimeoutError,
    SQLAlchemyError,
    ProgrammingError
)
from exceptions import (
    DBOperationalError,
    DBInterfaceError,
    DBTimeoutError,
    UniqueViolationError,
    ForeignKeyViolationError,
    NotNullViolationError,
    CheckViolationError,
    DataBaseError,
    InCorrectStmtError
)

if TYPE_CHECKING:
    from business_logic.user.user_manager import UserManager


class HandleException:
    """
    Класс декоратор для обработки ошибок базы данных
    """
    def __call__(self, cls: 'UserManager'):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value) and not attr_name.startswith('__'):
                setattr(cls, attr_name, self._wrap_method(attr_value))
        return cls

    @staticmethod
    def _wrap_method(method: Callable):
        """Метод обертка для методов репозитория с обработкой ошибок"""
        def wrapper(*args, **kwargs):
            try:
                result = method(*args, **kwargs)
                return result
            except ProgrammingError as e:
                """Исключения связанные ошибкой запроса"""
                raise InCorrectStmtError(str(e.statement), str(e.orig))
            except IntegrityError as e:
                """Исключения связанные с нарушение целостности данных"""
                operation: str = f'({method.__name__.replace('_', ' ')})'
                data = {'position_args': args, 'named_args': kwargs}
                stmt = e.statement
                cause = str(e.orig)
                if isinstance(e.orig, psycopg.errors.UniqueViolation):
                    raise UniqueViolationError(operation, data, stmt, cause)
                if isinstance(e.orig, psycopg.errors.ForeignKeyViolation):
                    raise ForeignKeyViolationError(operation, data, stmt, cause)
                if isinstance(e.orig, psycopg.errors.NotNullViolation):
                    raise NotNullViolationError(operation, data, stmt, cause)
                if isinstance(e.orig, psycopg.errors.CheckViolation):
                    raise CheckViolationError(operation, data, stmt, cause)
            except OperationalError as e:
                """Исключения связанные с неверным хостом, портом или бд не запущена"""
                raise DBOperationalError(str(e.orig))
            except InterfaceError as e:
                """Исключения связанные с неверным логином, пролем"""
                raise DBInterfaceError(str(e.orig))
            except TimeoutError as e:
                """Исключения связанные с таймаутом"""
                raise DBTimeoutError(str(e))
            except SQLAlchemyError as e:
                """Исключения связанные с другими ошибками sqlalchemy"""
                raise DataBaseError(f'неизвестная ошибка: {e}')
        return wrapper