from typing import Literal, Any
from uuid import UUID


class ValidationOrm(Exception):
    def __init__(self, orm_model, message: str | None = None):
        if message:
            result_message = f'Ошибка валидации ORM модели {orm_model}: {message}'
        else:
            result_message = f'Ошибка валидации ORM модели {orm_model}'
        self.orm_model = orm_model
        super().__init__(result_message)


class ValidationOrmDocError(ValidationOrm):
    def __init__(self, orm_model, message: str):
        result_message = f'Документация (обязательно): {message}'
        super().__init__(orm_model, result_message)


class ValidationOrmNotDocError(ValidationOrmDocError):
    def __init__(self, orm_model):
        result_message = 'отсутствует'
        super().__init__(orm_model, result_message)


class ValidationOrmIncorrectDocError(ValidationOrmDocError):
    MIN_COUNT_CHAR = 10

    def __init__(self, orm_model, current_count_char: int):
        result_message = (f'есть, но слишком короткая, '
                          f'нужно минимум {self.MIN_COUNT_CHAR} сим., '
                          f'сейчас: {current_count_char} сим.')
        super().__init__(orm_model, result_message)


class ValidationOrmTableNameError(ValidationOrm):
    def __init__(self, orm_model, message: str):
        result_message = f'Название таблицы (обязательно): {message}'
        super().__init__(orm_model, result_message)


class ValidationOrmNotTableNameError(ValidationOrmTableNameError):
    def __init__(self, orm_model):
        result_message = 'отсутствует'
        super().__init__(orm_model, result_message)


class ValidationOrmIncorrectTableNameError(ValidationOrmTableNameError):
    MIN_COUNT_CHAR = 3

    def __init__(self, orm_model, current_count_char: int):
        result_message = (f'есть, но слишком короткое, '
                          f'нужно минимум {type(self).MIN_COUNT_CHAR} сим., '
                          f'сейчас: {current_count_char} сим.')
        super().__init__(orm_model, result_message)


class DataBaseError(Exception):
    def __init__(self, message):
        message = f'Ошибка базы данных, {message}'
        super().__init__(message)


class ConnectionDBError(DataBaseError):
    def __init__(self, cause: str):
        message = f'не удалось подключиться по причине: {cause}'
        super().__init__(message)


class DBOperationalError(ConnectionDBError):
    def __init__(self, original: str):
        message = f'возможно неверный хост, порт, бд не запущена, оригинальная ошибка {original}'
        super().__init__(message)


class DBInterfaceError(ConnectionDBError):
    def __init__(self, original: str):
        message = f'неверный логин или пароль, оригинальная ошибка {original}'
        super().__init__(message)


class DBTimeoutError(ConnectionDBError):
    def __init__(self, original: str):
        message = f'сервер БД перегружен или не отвечает, оригинальная ошибка {original}'
        super().__init__(message)


class RecordNotFound(DataBaseError):
    def __init__(self, id: Any):
        message = f'не удалось найти запись с id: {id}'
        super().__init__(message)


class BreachIntegrity(DataBaseError):
    def __init__(
            self,
            operation: Literal['вставки', 'обновлении', 'удалении'],
            data: dict,
            stmt: object,
            cause: str
    ):
        self.operation = operation
        self.data = data
        self.stmt = stmt
        self.cause = cause
        message = (f'нарушение целостности данных при {operation} данных: {data}.\n'
                   f'Оригинальный sql запрос: {stmt}.\n'
                   f'Причина: {cause}')
        super().__init__(message)


class UniqueViolationError(BreachIntegrity):
    def __init__(
            self,
            operation: Literal['вставки', 'обновлении', 'удалении'],
            data: dict,
            stmt: object,
            cause: str
    ):
        self.operation = operation
        self.data = data
        self.stmt = stmt
        self.cause = cause
        message = f'ошибка уникальности: {cause}'
        super().__init__(operation, data, stmt, message)


class ForeignKeyViolationError(BreachIntegrity):
    def __init__(
            self,
            operation: Literal['вставки', 'обновлении', 'удалении'],
            data: dict,
            stmt: object,
            cause: str
    ):
        self.operation = operation
        self.data = data
        self.stmt = stmt
        self.cause = cause
        message = f'ошибка внешнего ключа: {cause}'
        super().__init__(operation, data, stmt, message)


class NotNullViolationError(BreachIntegrity):
    def __init__(
            self,
            operation: Literal['вставки', 'обновлении', 'удалении'],
            data: dict,
            stmt: object,
            cause: str
    ):
        self.operation = operation
        self.data = data
        self.stmt = stmt
        self.cause = cause
        message = f'столбец не может быть пустым (NOT NULL): {cause}'
        super().__init__(operation, data, stmt, message)


class CheckViolationError(BreachIntegrity):
    def __init__(
            self,
            operation: Literal['вставки', 'обновлении', 'удалении'],
            data: dict,
            stmt: object,
            cause: str
    ):
        self.operation = operation
        self.data = data
        self.stmt = stmt
        self.cause = cause
        message = f'данные не подходят под условия (Check): {cause}'
        super().__init__(operation, data, stmt, message)