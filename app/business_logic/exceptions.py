from uuid import UUID


class UserConnectionNotFound(Exception):
    """Не удачная попытка поиска подключений пользователя для отправки сообщения"""
    def __init__(self, target_id: str):
        self.message = f'Подключения пользователя {target_id} не найдено'
        super().__init__(self.message)


class SendMessageError(Exception):
    """Ошибка отправки сообщения"""
    def __init__(self, sender_id: str, target_id: str | UUID, cause: str):
        self.message = (f'Не удалось отправить сообщение '
                        f'пользователю(комнату: {target_id} от {sender_id} '
                        f'по причине: {cause}')
        super().__init__(self.message)


class RouteMessageError(Exception):
    """Ошибка маршрутизации сообщения"""
    def __init__(self, message_info):
        self.message = f'Не удалось маршрутизировать сообщение {message_info}'
        super().__init__(self.message)


class ChatNotFound(Exception):
    """Комната не найдена"""
    def __init__(self, chat_id: UUID):
        self.message = f'Не удалось найти чат {chat_id} для broadcast'
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """Информация о пользователе не найдена"""
    def __init__(self, user_id: str):
        self.message = f'Информация о пользователе {user_id} не передана в метод для получения или создание активной сессии'
        super().__init__(self.message)


class CheckPswError(Exception):
    """Переданный пароль не совпадает с сохраненным"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.message = f'Передан неверный пароль для пользователя {user_id}'
        super().__init__(self.message)


class CheckMasterPswError(Exception):
    """Переданный пароль не совпадает с мастер паролем"""
    def __init__(self):
        self.message = f'Передан неверный мастер пароль'
        super().__init__(self.message)


class SyncKeyError(Exception):
    """Неудачная попытка синхронизации ключей между сессиями"""
    def __init__(self, user_id: str):
        self.message = f'Не удалось синхронизировать ключи для пользователя {user_id}'
        super().__init__(self.message)


class PermissionFileDownError(Exception):
    """Нет прав для загрузки файлов"""
    def __init__(self, user_id: str, file_id: UUID):
        self.message = f'У пользователя {user_id} нет прав на доступ к файлу {file_id}'
        super().__init__(self.message)


class RefreshTokenIdNotFound(Exception):
    """Не удалось найти refresh токен по id в white list"""
    def __init__(self, user_id: str, token_id: UUID):
        self.message = (f'Не удалось найти токен у пользователя {user_id} '
                   f'по id {token_id} в white list')
        super().__init__(self.message)


class SessionKeyNotFound(Exception):
    """Не удалось найти session key пользователя"""
    def __init__(self, user_id: str, session_id: UUID):
        self.message = (f'Не удалось найти session id у пользователя {user_id} '
                   f'по session_id {session_id} в кеше')
        super().__init__(self.message)


class SaveIdRefreshTokenWhiteListError(Exception):
    """Неудачная попытка сохранения id refresh токена"""
    def __init__(self, user_id: str):
        self.message = f'Не удалось сохранить id refresh токена пользователя {user_id} в white list'
        super().__init__(self.message)


class SaveSessionKeyError(Exception):
    """Неудачная попытка сохранения сессионного ключа"""
    def __init__(self, user_id: str, session_id: UUID):
        self.message = f'Не удалось сохранить сессионный ключ пользователя {user_id}'
        super().__init__(self.message)


class UserNotFoundInRoom(Exception):
    """Не удалось найти пользователя в комнате"""
    def __init__(self, user_id: str, room_id: UUID):
        self.message = f'Не удалось найти пользователя {user_id} в комнате {room_id}'
        super().__init__(self.message)


class RoomNotFound(Exception):
    """Комната не найдена"""
    def __init__(self, room_id: UUID):
        self.message = f'Не удалось найти комнату {room_id}'
        super().__init__(self.message)


class RefreshTokenInActive(Exception):
    """Refresh токен больше не активен"""
    def __init__(self, user_id: str, token_id):
        self.user_id = user_id
        self.message = f'Refresh токен больше не активен для пользователя {user_id}, токен id: {token_id}'
        super().__init__(self.message)


class MessageOwnerInCorrect(Exception):
    """Попытка удалить сообщение, которое не принадлежит отправителю"""
    def __init__(self, message_id: UUID, sender_id: str):
        self.message = (f'Попытка удалить сообщение {message_id}, '
                        f'которое не принадлежит отправителю {sender_id}')
        super().__init__(self.message)


class VerifyCodeStorageError(Exception):
    """Не удалось получить код подтверждения из кеша"""
    def __init__(self,):
        self.message = ('Не удалось найти код подтверждения, '
                        'т.к. сервис временно недоступен')
        super().__init__(self.message)


class VerifyCodeInCorrect(Exception):
    """Введенный код подтверждения неверный"""
    def __init__(self,):
        self.message = 'Введенный код подтверждения неверный'
        super().__init__(self.message)