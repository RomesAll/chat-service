from pydantic import BaseModel, Field, ConfigDict, SecretStr, EmailStr
from fastapi.websockets import WebSocket
from base import (
    BaseDtoOrmRecordGetResponse,
    BaseDtoOrmRecordPostRequest,
    BaseDtoOrmRecordPutResponse,
    BaseDtoOrmRecordDeleteResponse, BaseDtoOrmRecord
)


class UserDtoGetResponse(BaseDtoOrmRecordGetResponse):
    """User DTO для операции получения (Get) информации о пользователе"""
    user_name: str
    bio: str
    years_old: int
    email: EmailStr


class UserDtoPostRequest(UserDtoGetResponse, BaseDtoOrmRecordPostRequest):
    """User DTO для операции добавления (Post) информации о пользователе"""
    password: SecretStr


class UserDtoUpdateRequest(BaseDtoOrmRecordPutResponse):
    """User DTO для операции обновления (Put) информации о пользователе"""
    user_name: str = Field(None)
    bio: str = Field(None)
    years_old: int = Field(None)
    is_deleted: bool = Field(None)


class UserDtoDeleteRequest(BaseDtoOrmRecordDeleteResponse):
    """User DTO для операции удаления (Delete) информации о пользователе"""
    pass


class UserDtoBriefInfo(BaseDtoOrmRecord):
    """User DTO для хранения краткой информации о пользователе"""
    user_name: str
    years_old: int
    email: str


class UserDtoChangePsw(BaseDtoOrmRecord):
    """User DTO для смены старого пароля на новый"""
    old_password: SecretStr
    new_password: SecretStr
    repeat_password: SecretStr


class ActiveSession(BaseModel):
    """User DTO для хранения активных подключений (websocket соединений) пользователя"""
    info: UserDtoBriefInfo
    websockets: set[WebSocket] = Field(default_factory=set)
    model_config = ConfigDict(arbitrary_types_allowed=True)
