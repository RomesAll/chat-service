from typing import Callable
import psycopg.errors
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    InterfaceError,
    TimeoutError,
    SQLAlchemyError,
    ProgrammingError
)
from app.data_access.exceptions import (
    DBOperationalError,
    DBInterfaceError,
    DBTimeoutError,
    UniqueViolationError,
    ForeignKeyViolationError,
    NotNullViolationError,
    CheckViolationError,
    DataBaseError,
    InCorrectStmtError, BreachIntegrity
)
from shared.log_config import LogMixin


class HandleSqlAlchemyException(LogMixin):
    """
    Класс декоратор для обработки ошибок sqlalchemy
    """
    def __call__(self, cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value) and not attr_name.startswith('__'):
                setattr(cls, attr_name, self._wrap_method(attr_value))
        return cls

    def _wrap_method(self, method: Callable):
        """Метод обертка для методов репозитория с обработкой ошибок"""
        def wrapper(*args, **kwargs):
            try:
                result = method(*args, **kwargs)
                return result
            except ProgrammingError as e:
                """Исключения связанные ошибкой запроса"""
                exc = InCorrectStmtError(str(e.statement), str(e.orig))
                self.log_error(exc.message)
                raise exc
            except IntegrityError as e:
                """Исключения связанные с нарушение целостности данных"""
                operation: str = f'({method.__name__.replace('_', ' ')})'
                data = {'position_args': args, 'named_args': kwargs}
                stmt = e.statement
                cause = str(e.orig)
                if isinstance(e.orig, psycopg.errors.UniqueViolation):
                    exc = UniqueViolationError(operation, data, stmt, cause)
                    self.log_error(exc.message)
                    raise exc
                if isinstance(e.orig, psycopg.errors.ForeignKeyViolation):
                    exc = ForeignKeyViolationError(operation, data, stmt, cause)
                    self.log_error(exc.message)
                    raise exc
                if isinstance(e.orig, psycopg.errors.NotNullViolation):
                    exc = NotNullViolationError(operation, data, stmt, cause)
                    self.log_error(exc.message)
                    raise exc
                if isinstance(e.orig, psycopg.errors.CheckViolation):
                    exc = CheckViolationError(operation, data, stmt, cause)
                    self.log_error(exc.message)
                    raise exc
                exc = BreachIntegrity(operation, data, stmt, cause)
                self.log_error(exc.message)
                raise exc
            except OperationalError as e:
                """Исключения связанные с неверным хостом, портом или бд не запущена"""
                exc = DBOperationalError(str(e.orig))
                self.log_error(exc.message)
                raise exc
            except InterfaceError as e:
                """Исключения связанные с неверным логином, пролем"""
                exc = DBInterfaceError(str(e.orig))
                self.log_error(exc.message)
                raise exc
            except TimeoutError as e:
                """Исключения связанные с таймаутом"""
                exc = DBTimeoutError(str(e))
                self.log_error(exc.message)
                raise exc
            except SQLAlchemyError as e:
                """Исключения связанные с другими ошибками sqlalchemy"""
                exc = DataBaseError(f'неизвестная ошибка: {e}')
                self.log_error(exc.message)
                raise exc
        return wrapper