from uuid import UUID
from shared.dtos.message import BaseMessageDtoPostRequest


class UserConnectionNotFound(Exception):
    """Не удачная попытка поиска подключений пользователя для отправки сообщения"""
    def __init__(self, target_id: UUID):
        message = f'Подключения пользователя {target_id} не найдено'
        super().__init__(message)


class SendMessageError(Exception):
    """Ошибка отправки сообщения"""
    def __init__(self, sender_id: UUID, target_id: UUID, cause: str):
        message = (f'Не удалось отправить сообщение '
                        f'пользователю: {target_id} от {sender_id} '
                        f'по причине: {cause}')
        super().__init__(message)


class RouteMessageError(Exception):
    """Ошибка маршрутизации сообщения"""
    def __init__(self, message_info: BaseMessageDtoPostRequest):
        message = f'Не удалось маршрутизировать сообщение {message_info}, типа: {message_info.type}'
        super().__init__(message)


class ChatNotFound(Exception):
    """Комната не найдена"""
    def __init__(self, chat_id: UUID):
        message = f'Не удалось найти чат {chat_id} для broadcast'
        super().__init__(message)
