from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ActionType:
    """Типы действий для аудита"""
    GET_SERVER_PUBLIC_KEY = 'Получение публичного ключа сервера'
    GET_SESSION_ID = 'Получение id сессии'
    GET_USER_PUBLIC_KEY = 'Получение публичного ключа пользователя'
    GET_USER_PRIVATE_KEYS = 'Получение приватных ключей пользователя'
    SEND_PRIVATE_MESSAGE = 'Отправка приватного сообщения'
    SEND_GROUP_MESSAGE = 'Отправка сообщения в группу (комнату)'
    DELETE_MSG = 'Удаление сообщения'


class AuditPostDto(BaseModel):
    """DTO для сохранения информации о действиях в аудит-сервис """
    user_id: str
    action: ActionType
    target_api: str
    timestamp: datetime = Field(default_factory=lambda : datetime.now(tz=timezone.utc))
    ip: str
    user_agent: str