from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from fastapi.websockets import WebSocket
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostRequest,
    BaseDtoUpdateRequest,
    BaseDtoDeleteRequest
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


class UserDtoUpdateRequest(BaseDtoUpdateRequest):
    """Dto модель для хранения данных о пользователях для обновления"""
    user_name: str
    bio: str
    years_old: int
    is_deleted: bool


class UserDtoDeleteRequest(BaseDtoDeleteRequest):
    """Dto модель для хранения данных о пользователях для удаления"""
    pass


class UserInfo(BaseModel):
    """Информация о пользователей"""
    id: UUID
    user_name: str
    years_old: int
    is_deleted: bool
    email: str
    model_config = ConfigDict(extra='ignore')


class ActiveSession(BaseModel):
    """Активные сессии пользователя"""
    info: UserInfo
    websockets: set[WebSocket] = Field(default_factory=set)
    model_config = ConfigDict(arbitrary_types_allowed=True)