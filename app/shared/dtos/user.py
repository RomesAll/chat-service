from uuid import UUID
from pydantic import BaseModel
from fastapi.websockets import WebSocket

from .base import (
    BaseDtoGetResponse,
    BaseDtoPostRequest
)


class UserDtoGetResponse(BaseDtoGetResponse):
    """Dto модель для хранения полученной информации о пользователях"""
    user_name: str
    bio: str
    years_old: int
    email: str
    password: str


class UserDtoPostRequest(BaseDtoPostRequest):
    """Dto модель для хранения данных о пользователях для сохранения"""
    user_name: str
    bio: str
    years_old: int
    email: str
    password: str


class UserDtoUpdateRequest(UserDtoPostRequest):
    """Dto модель для хранения данных о пользователях для обновления"""
    user_name: str
    bio: str
    years_old: int
    is_deleted: bool


class UserDtoDeleteRequest(BaseDtoPostRequest):
    """Dto модель для хранения данных о пользователях для удаления"""
    pass


class UserInfo(BaseModel):
    """Информация о пользователей"""
    id: UUID
    user_name: str
    years_old: int
    is_deleted: bool
    email: str


class ActiveSession(BaseModel):
    """Активные сессии пользователя"""
    info: UserInfo
    websockets: set[WebSocket]