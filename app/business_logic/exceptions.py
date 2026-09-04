from uuid import UUID


class UserConnectionNotFound(Exception):
    """Не удачная попытка поиска подключений пользователя для отправки сообщения"""
    def __init__(self, target_id: str):
        message = f'Подключения пользователя {target_id} не найдено'
        super().__init__(message)


class SendMessageError(Exception):
    """Ошибка отправки сообщения"""
    def __init__(self, sender_id: str, target_id: str | UUID, cause: str):
        message = (f'Не удалось отправить сообщение '
                        f'пользователю(комнату: {target_id} от {sender_id} '
                        f'по причине: {cause}')
        super().__init__(message)


class RouteMessageError(Exception):
    """Ошибка маршрутизации сообщения"""
    def __init__(self, message_info):
        message = f'Не удалось маршрутизировать сообщение {message_info}'
        super().__init__(message)


class ChatNotFound(Exception):
    """Комната не найдена"""
    def __init__(self, chat_id: UUID):
        message = f'Не удалось найти чат {chat_id} для broadcast'
        super().__init__(message)


class UserNotFoundError(Exception):
    """Информация о пользователе не найдена"""
    def __init__(self, user_id: str):
        message = f'Информация о пользователе {user_id} не передана в метод для получения или создание активной сессии'
        super().__init__(message)


class CheckPswError(Exception):
    """Переданный пароль не совпадает с сохраненным"""
    def __init__(self, user_id: str):
        message = f'Передан неверный пароль для пользователя {user_id}'
        super().__init__(message)


class SyncKeyError(Exception):
    """Неудачная попытка синхронизации ключей между сессиями"""
    def __init__(self, user_id: str):
        message = f'Не удалось синхронизировать ключи для пользователя {user_id}'
        super().__init__(message)


class PermissionFileDownError(Exception):
    """Нет прав для загрузки файлов"""
    def __init__(self, user_id: str, file_id: UUID):
        message = f'У пользователя {user_id} нет прав на доступ к файлу {file_id}'
        super().__init__(message)


class RefreshTokenIdNotFound(Exception):
    """Не удалось найти refresh токен по id в white list"""
    def __init__(self, user_id: str, token_id: UUID):
        message = (f'Не удалось найти токен у пользователя {user_id} '
                   f'по id {token_id} в white list')
        super().__init__(message)


class SessionKeyNotFound(Exception):
    """Не удалось найти session key пользователя"""
    def __init__(self, user_id: str, session_id: UUID):
        message = (f'Не удалось найти session id у пользователя {user_id} '
                   f'по session_id {session_id} в кеше')
        super().__init__(message)


class SaveIdRefreshTokenWhiteListError(Exception):
    """Неудачная попытка сохранения id refresh токена"""
    def __init__(self, user_id: str):
        message = f'Не удалось сохранить id refresh токена пользователя {user_id} в white list'
        super().__init__(message)


class SaveSessionKeyError(Exception):
    """Неудачная попытка сохранения сессионного ключа"""
    def __init__(self, user_id: str, session_id: UUID):
        message = f'Не удалось сохранить сессионный ключ пользователя {user_id}'
        super().__init__(message)