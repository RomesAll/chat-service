from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ActionType(str, Enum):
    """Типы действий для аудита"""
    GET_SERVER_PUBLIC_KEY = 'Получение публичного ключа сервера'
    GET_SESSION_ID = 'Получение id сессии'
    GET_USER_PUBLIC_KEY = 'Получение публичного ключа пользователя'
    GET_USER_PRIVATE_KEYS = 'Получение приватных ключей пользователя'
    SEND_PRIVATE_MESSAGE = 'Отправка приватного сообщения'
    SEND_GROUP_MESSAGE = 'Отправка сообщения в группу (комнату)'
    DELETE_MSG = 'Удаление сообщения'
    LOGIN = 'Прохождение авторизации/аутентификации'
    REGISTER = 'Прохождение регистрации'
    REFRESH_TOKENS = 'Обновление токенов'
    LOGOUT = 'Выход из сессии'
    SYNC_DEVICES_USER = 'Синхронизация устройств пользователя'
    SAVE_PUBLIC_KEY = 'Сохранение публичного ключа пользователя'
    SAVE_PRIVATE_KEY = 'Сохранение приватного ключа пользователя'
    DOWNLOAD_FILE = 'Загрузка файлов'
    GET_HISTORY_MSG = 'Получение истории сообщений'
    SAVE_NEW_ROOM = 'Сохранить новую комнату'
    ADD_USER_IN_ROOM = 'Добавить пользователя в комнату'
    GET_PUBLIC_KEY_USER_IN_ROOM = 'Получение всех публичных ключей пользователей в комнате'
    SOFT_DELETE_USER = 'Мягкое удаление пользователя'
    HARD_DELETE_USER = 'Жесткое удаление пользователя'
    RECOVERY_USER = 'Восстановление пользователей'
    GET_USERS = 'Получение пользователей'
    GET_ONE_USER = 'Получить одного пользователя'
    UPDATE_USER = 'Обновление пользователей'
    HANDSHAKE = 'Выполнение рукопожатия с сервером'
    DEACTIVATE = 'Отключение пользователя'
    VERIFY_CODE = 'Подтверждение сообщения'
    REFRESH_VERIFY_CODE = 'Обновление кода подтверждения'


class AuditPostDto(BaseModel):
    """DTO для сохранения информации о действиях в аудит-сервис """
    user_id: str | None = None
    action: ActionType | None = None
    target_api: str
    timestamp: datetime = Field(default_factory=lambda : datetime.now(tz=timezone.utc))
    ip: str
    user_agent: str
    successfully: bool = True
    exceptions: str | None = None
    result: Any | None = None