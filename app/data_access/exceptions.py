from typing import Any


class ValidationOrm(Exception):
    """Ошибки валидации orm моделей"""
    def __init__(self, orm_model, message: str | None = None):
        if message:
            result_message = f'Ошибка валидации ORM модели {orm_model}: {message}'
        else:
            result_message = f'Ошибка валидации ORM модели {orm_model}'
        self.orm_model = orm_model
        self.result_message = result_message
        super().__init__(result_message)


class ValidationOrmDocError(ValidationOrm):
    """Ошибки валидации документации orm моделей"""
    def __init__(self, orm_model, message: str):
        result_message = f'Документация (обязательно): {message}'
        super().__init__(orm_model, result_message)


class ValidationOrmNotDocError(ValidationOrmDocError):
    """Отсутствие документации для orm моделей"""
    def __init__(self, orm_model):
        result_message = 'отсутствует'
        super().__init__(orm_model, result_message)


class ValidationOrmIncorrectDocError(ValidationOrmDocError):
    """Некорректная документация для orm моделей"""
    MIN_COUNT_CHAR = 10

    def __init__(self, orm_model, current_count_char: int):
        result_message = (f'есть, но слишком короткая, '
                          f'нужно минимум {self.MIN_COUNT_CHAR} сим., '
                          f'сейчас: {current_count_char} сим.')
        super().__init__(orm_model, result_message)


class ValidationOrmTableNameError(ValidationOrm):
    """Ошибка в названии таблицы у orm моделей"""
    def __init__(self, orm_model, message: str):
        result_message = f'Название таблицы (обязательно): {message}'
        super().__init__(orm_model, result_message)


class ValidationOrmNotTableNameError(ValidationOrmTableNameError):
    """Отсутствует название таблицы у orm моделей"""
    def __init__(self, orm_model):
        result_message = 'отсутствует'
        super().__init__(orm_model, result_message)


class ValidationOrmIncorrectTableNameError(ValidationOrmTableNameError):
    """Ошибка валидации таблицы у orm моделей"""
    MIN_COUNT_CHAR = 3

    def __init__(self, orm_model, current_count_char: int):
        result_message = (f'есть, но слишком короткое, '
                          f'нужно минимум {type(self).MIN_COUNT_CHAR} сим., '
                          f'сейчас: {current_count_char} сим.')
        super().__init__(orm_model, result_message)


class DataBaseError(Exception):
    """Базовая ошибка базы данных"""
    def __init__(self, message):
        self.message = f'Ошибка базы данных, {message}'
        super().__init__(message)


class ConnectionDBError(DataBaseError):
    """Ошибка подключения к базе данных"""
    def __init__(self, cause: str):
        message = f'не удалось подключиться по причине: {cause}'
        super().__init__(message)


class DBOperationalError(ConnectionDBError):
    """Неверный хост, порт или бд не запущена"""
    def __init__(self, original: str):
        message = f'возможно неверный хост, порт, бд не запущена, оригинальная ошибка {original}'
        super().__init__(message)


class DBInterfaceError(ConnectionDBError):
    """Неверный логин или пароль для бд"""
    def __init__(self, original: str):
        message = f'неверный логин или пароль, оригинальная ошибка {original}'
        super().__init__(message)


class DBTimeoutError(ConnectionDBError):
    """Ошибка таймаута бд"""
    def __init__(self, original: str):
        message = f'сервер БД перегружен или не отвечает, оригинальная ошибка {original}'
        super().__init__(message)


class RecordNotFound(DataBaseError):
    """Запись в бд не найдена"""
    def __init__(self, id: Any):
        message = f'не удалось найти запись с id: {id}'
        super().__init__(message)


class InCorrectStmtError(DataBaseError):
    """Неверный stmt для бд"""
    def __init__(
            self,
            stmt: object,
            cause: str
    ):
        self.stmt = stmt
        self.cause = cause
        message = (f'неверный запрос.\n'
                   f'Оригинальный sql запрос: {stmt}.\n'
                   f'Причина: {cause}')
        super().__init__(message)


class BreachIntegrity(DataBaseError):
    """Ошибки связанные с нарушением целостности бд"""
    def __init__(
            self,
            operation: str,
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
    """Ошибка уникльности"""
    def __init__(
            self,
            operation: str,
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
    """Ошибка во внешних ключах"""
    def __init__(
            self,
            operation: str,
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
    """Ошибка not null столбцов"""
    def __init__(
            self,
            operation: str,
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
    """Ошибка в проверке на стороне бд в Check"""
    def __init__(
            self,
            operation: str,
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