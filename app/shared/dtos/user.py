from typing import Self
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, SecretStr, EmailStr, model_validator
from fastapi.websockets import WebSocket
from .base import (
    BaseDtoGetResponse,
    BaseDtoClientRequest,
    BaseDtoPostDeleteRequest,
    BaseDtoPutPathRequest
)


class UserDtoGetResponse(BaseDtoGetResponse):
    """User DTO для операции получения (Get) информации о пользователе"""
    user_name: str
    bio: str = Field(None)
    years_old: int = Field(None)
    email: EmailStr


class UserDtoPostRequest(BaseDtoPostDeleteRequest):
    """User DTO для операции добавления (Post) информации о пользователе"""
    user_name: str
    email: EmailStr
    password: SecretStr = Field(..., exclude=True)
    repeat_password: SecretStr = Field(..., exclude=True)


class UserDtoUpdateRequest(BaseDtoPutPathRequest):
    """User DTO для операции обновления (Put) информации о пользователе"""
    user_name: str | None = Field(default=None, examples=[None])
    bio: str | None = Field(default=None, examples=[None])
    years_old: int | None = Field(default=None, examples=[None])
    is_deleted: bool | None = Field(default=None, examples=[None])


class UserDtoDeleteRequest(BaseDtoPostDeleteRequest):
    """User DTO для операции удаления (Delete) информации о пользователе"""
    pass


class UserDtoBriefInfo(BaseModel):
    """User DTO для хранения краткой информации о пользователе"""
    id: UUID
    user_name: str
    years_old: int
    email: str


class UserDtoChangePsw(BaseDtoClientRequest):
    """User DTO для смены старого пароля на новый"""
    old_password: SecretStr
    new_password: SecretStr
    repeat_password: SecretStr


class ActiveSession(BaseModel):
    """User DTO для хранения активных подключений (websocket соединений) пользователя"""
    info: UserDtoBriefInfo
    websockets: set[WebSocket] = Field(default_factory=set)
    model_config = ConfigDict(arbitrary_types_allowed=True)
