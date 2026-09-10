from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, SecretStr, Field


class LoginDtoRequest(BaseModel):
    """DTO для входа в систему"""
    user_id: str
    password: SecretStr


class SendType(str, Enum):
    PHONE = 'телефон'
    EMAIL = 'email'


class LoginOrRegisterDtoResponse(BaseModel):
    """DTO для получения информации о пользователе после входа или регистрации"""
    send_code: SendType
    time_send: datetime = Field(default_factory=lambda : datetime.now(tz=timezone.utc))


class VerifyCodeRequest(BaseModel):
    """DTO для передачи и проверки кода подтверждения"""
    user_id: str
    email: str
    code: int


class RefreshVerifyCodeRequest(BaseModel):
    """DTO для обновления кода"""
    user_id: str
    email: str