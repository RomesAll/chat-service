from typing import Self
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, SecretStr, EmailStr, model_validator, ValidationError, \
    field_serializer
from fastapi.websockets import WebSocket
from app.data_access.database.models.user import RoleEnum
from .base import (
    BaseDtoGetResponse,
    BaseDtoPostDeleteRequest,
    BaseDtoPutPathRequest
)
from .auth import SendType


class UserDtoGetResponse(BaseDtoGetResponse):
    """User DTO для операции получения (Get) информации о пользователе"""
    id: str
    user_name: str
    role: RoleEnum
    bio: str = Field(None)
    years_old: int = Field(None)
    email: EmailStr
    phone: str
    model_config = ConfigDict(extra='allow')

    def get_contact_details(self, send_type: SendType) -> str | None:
        if send_type.EMAIL:
            return self.email
        else:
            return self.phone

    def get_success_send_msg(self, send_type: SendType) -> str:
        msg = f'Код подтверждения был выслан на {send_type.value}, '
        if send_type == SendType.EMAIL:
            msg += f'по адресу: {self.email}'
        elif send_type == SendType.PHONE:
            msg += f'по номеру: {self.email}'
        else:
            raise Exception
        return msg


class UserDtoBaseInfoPostRequest(BaseDtoPostDeleteRequest):
    """User DTO для операции добавления (Post) информации о пользователе (базовая информация)"""
    id: str
    user_name: str
    email: EmailStr
    phone: str
    password: SecretStr


class UserDtoRegisterRequest(UserDtoBaseInfoPostRequest):
    """User DTO для операции добавления (Post) информации о пользователе"""
    repeat_password: SecretStr = Field(..., exclude=True)

    @model_validator(mode='after')
    def validate_psw(self) -> Self:
        if self.repeat_password != self.password:
            raise ValidationError('Пароли не совпадают')
        return self


class UserDtoPostRequestWithRole(UserDtoBaseInfoPostRequest):
    """User DTO для операции добавления (Post) информации о пользователе с ролью"""
    role: RoleEnum


class UserDtoUpdateRequest(BaseDtoPutPathRequest):
    """User DTO для операции обновления (Put) информации о пользователе"""
    user_name: str | None = Field(default=None, examples=[None])
    bio: str | None = Field(default=None, examples=[None])
    years_old: int | None = Field(default=None, examples=[None])


class UserDtoDeleteRequest(BaseDtoPostDeleteRequest):
    """User DTO для операции удаления (Delete) информации о пользователе"""
    id: str


class UserDtoBriefInfo(BaseModel):
    """User DTO для хранения краткой информации о пользователе"""
    id: str
    user_name: str
    years_old: int | None = None
    email: str
    phone: str


class UserDtoChangePsw(BaseModel):
    """User DTO для смены старого пароля на новый"""
    id: str
    old_password: SecretStr
    new_password: SecretStr
    repeat_password: SecretStr


class ActiveSession(BaseModel):
    """User DTO для хранения активных подключений (websocket соединений) пользователя"""
    info: UserDtoBriefInfo
    user_sessions: dict[UUID, WebSocket]
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes = True)


class VerifyCodeResponse(BaseModel):
    user_info: UserDtoGetResponse
    access_token: str
    refresh_token: str