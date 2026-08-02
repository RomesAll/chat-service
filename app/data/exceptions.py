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